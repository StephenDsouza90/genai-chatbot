import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from haystack import Pipeline, component
from haystack.components.embedders import (
    AzureOpenAITextEmbedder,
    AzureOpenAIDocumentEmbedder,
)
from haystack.components.generators import AzureOpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.dataclasses import (
    Document as HaystackDocument,
    ChatMessage as HaystackChatMessage,
)
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.utils import Secret
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.retrievers.pgvector.embedding_retriever import (
    PgvectorEmbeddingRetriever,
)

from src.core.config import Settings


@component
class MetadataAdder:
    """
    Component for adding metadata to documents.

    This component is used to add metadata to documents before they are indexed.
    It is a simple component that adds the metadata to the documents.

    Attributes:
        documents: The documents to add metadata to.
        meta: The metadata to add to the documents.

    Methods:
        run: Add metadata to documents.
    """

    @component.output_types(documents=List[HaystackDocument])
    def run(
        self,
        documents: List[HaystackDocument],
        meta: Dict[str, Any] | None = None,
    ) -> Dict[str, List[HaystackDocument]]:
        """
        Add metadata to documents.

        Args:
            documents: The documents to add metadata to.
            meta: The metadata to add to the documents.
        """
        if meta:
            for doc in documents:
                # Ensure meta exists and update
                if doc.meta is None:
                    doc.meta = {}
                doc.meta.update(meta)
        return {"documents": documents}


class HaystackService:
    """
    Service for handling Haystack operations.

    This service is responsible for initializing the Haystack pipelines and document store.
    It also provides methods for processing documents and querying the RAG pipeline.

    Attributes:
        settings: The application settings.
        document_store: The document store for storing documents.
        indexing_pipeline: The pipeline for indexing documents.
        rag_pipeline: The pipeline for querying documents.

    Methods:
        process_document: Process a document using the indexing pipeline.
        query: Query the RAG pipeline.
    """
    def __init__(self):
        """
        Initialize the HaystackService with the necessary settings.

        This method initializes the HaystackService with the necessary settings.
        It prepares the connection string for the document store and initializes the document store,
        indexing pipeline, and RAG pipeline.
        """
        self.settings = Settings()

        # Prepare a psycopg-compatible connection string for Pgvector
        pg_conn_str = self.settings.DATABASE_URL or ""
        if pg_conn_str.startswith("postgresql+asyncpg://"):
            pg_conn_str = pg_conn_str.replace(
                "postgresql+asyncpg://", "postgresql://", 1
            )

        # Initialize PGVector document store (ensure dimension matches embedder)
        self._init_document_store(pg_conn_str)

        # Initialize pipelines
        self._init_indexing_pipeline()
        self._init_rag_pipeline()

    def _init_document_store(self, pg_conn_str: str):
        """
        Initialize the document store.

        Args:
            pg_conn_str: The connection string for the document store.
        """
        self.document_store = PgvectorDocumentStore(
            connection_string=Secret.from_token(pg_conn_str),
            table_name="haystack_documents",
            embedding_dimension=self.settings.EMBEDDING_DIMENSION,
            vector_function="cosine_similarity",
            # recreate_table=True,
        )

    def _init_indexing_pipeline(self):
        """
        Initialize the document indexing pipeline.

        This pipeline is used to index documents into the document store.
        It converts the PDF documents into Haystack documents and adds metadata to them.
        It then embeds the documents and writes them to the document store.
        """
        self.indexing_pipeline = Pipeline()

        # Add components
        self.indexing_pipeline.add_component("converter", PyPDFToDocument())
        self.indexing_pipeline.add_component(
            "splitter",
            DocumentSplitter(
                split_by=self.settings.SPLIT_BY,
                split_length=self.settings.SPLIT_LENGTH,
                split_overlap=self.settings.SPLIT_OVERLAP,
            ),
        )
        self.indexing_pipeline.add_component("meta_adder", MetadataAdder())
        self.indexing_pipeline.add_component(
            "embedder",
            AzureOpenAIDocumentEmbedder(
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
                api_version=self.settings.API_VERSION,
                azure_deployment=self.settings.EMBEDDING_MODEL,
                api_key=Secret.from_token(self.settings.OPENAI_API_KEY),
            ),
        )
        self.indexing_pipeline.add_component(
            "writer", DocumentWriter(document_store=self.document_store)
        )

        # Connect components
        self.indexing_pipeline.connect("converter", "splitter")
        self.indexing_pipeline.connect("splitter", "meta_adder.documents")
        self.indexing_pipeline.connect("meta_adder", "embedder")
        self.indexing_pipeline.connect("embedder", "writer")

    def _init_rag_pipeline(self):
        """
        Initialize the RAG pipeline.

        This pipeline is used to query the document store for relevant documents.
        It embeds the question and retrieves the top K most relevant documents.
        It then passes the documents to the prompt builder to generate a response.
        """
        self.rag_pipeline = Pipeline()

        # Add components
        self.rag_pipeline.add_component(
            "embedder",
            AzureOpenAITextEmbedder(
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
                api_version=self.settings.API_VERSION,
                azure_deployment=self.settings.EMBEDDING_MODEL,
                api_key=Secret.from_token(self.settings.OPENAI_API_KEY),
            ),
        )
        self.rag_pipeline.add_component(
            "retriever",
            PgvectorEmbeddingRetriever(
                document_store=self.document_store,
                top_k=self.settings.TOP_K
            ),
        )
        self.rag_pipeline.add_component(
            "prompt_builder", PromptBuilder(template=self._get_prompt_template())
        )
        self.rag_pipeline.add_component(
            "llm",
            AzureOpenAIGenerator(
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
                api_version=self.settings.API_VERSION,
                azure_deployment=self.settings.CHAT_MODEL,
                api_key=Secret.from_token(self.settings.OPENAI_API_KEY),
                # Parameters for better control:
                generation_kwargs={
                    "temperature": self.settings.TEMPERATURE,
                    "max_tokens": self.settings.MAX_TOKENS,
                    "top_p": self.settings.TOP_P,
                    "presence_penalty": self.settings.PRESENCE_PENALTY,
                    "frequency_penalty": self.settings.FREQUENCY_PENALTY,
                },
            ),
        )

        # Connect components
        self.rag_pipeline.connect("embedder.embedding", "retriever.query_embedding")
        self.rag_pipeline.connect("retriever", "prompt_builder.documents")
        self.rag_pipeline.connect("prompt_builder", "llm")

    def _get_prompt_template(self) -> str:
        """
        Get the prompt template for RAG.

        This template is used to generate a response to a user's question.
        It is a Jinja2 template that is used to generate a response to a user's question.
        """
        return """
        Current date: {{ current_date }}

        Context Documents:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}
        
        Chat History:
        {% for message in chat_history %}
            {{ message.role }}: {{ message.content }}
        {% endfor %}
        
        Question: {{ question }}

        Rules:
        1. Only use information from the provided documents and chat history.
        - If insufficient information, reply: "I cannot answer this question based on the provided context." 
        - Then briefly explain why.
        2. Resolve unclear references (e.g., “he”, “she”, “it”) from chat history. If still ambiguous, state uncertainty.
        3. Do not fabricate facts beyond reasonable inference.
        4. For dates/durations, use the current date unless another date is specified.
        5. Provide a comprehensive, numbered, step-by-step guide that preserves all enumerated steps found in the context. Do not omit steps. Maintain the original order when possible and include field names and button/icon actions exactly as stated.
        6. After answering, ask 1–2 relevant follow-up questions based on the documents that the user has not yet asked.
        - Examples: “Do you also want me to check...?”, “Would you like me to explain how this relates to...?”

        Answering Process:
        1. Search documents for relevant facts.
        2. Check chat history for missing context or references.
        3. Provide the most accurate answer possible.
        4. If unsure, explain uncertainty.
        5. End with proactive follow-up questions.
        """

    async def process_document(
        self, file_content: bytes, filename: str, document_id: UUID
    ) -> Dict[str, Any]:
        """
        Process a document using Haystack pipeline.

        This method is used to process a document using the indexing pipeline.
        It saves the file temporarily and runs the indexing pipeline.

        Args:
            file_content: The content of the document.
            filename: The name of the document.
            document_id: The ID of the document.

        Returns:
            Dict[str, Any]: The result of the indexing pipeline.
        """
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Run indexing pipeline
            result = self.indexing_pipeline.run(
                {
                    "converter": {"sources": [temp_file_path]},
                    "meta_adder": {
                        "meta": {
                            "filename": filename,
                            "document_id": str(document_id),
                            "source": filename,
                        }
                    },
                }
            )

            return {
                "documents_processed": result["writer"]["documents_written"],
                "success": True,
            }

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    async def query(
        self,
        question: str,
        document_ids: List[UUID],
        chat_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Query documents using RAG pipeline.

        This method is used to query the document store for relevant documents.
        It filters the documents by the document_ids and runs the RAG pipeline.

        Args:
            question: The question to query the document store with.
            document_ids: The IDs of the documents to query the document store with.
            chat_history: The chat history to use for the RAG pipeline.

        Returns:
            Dict[str, Any]: The result of the RAG pipeline.
        """
        # Filter documents by document_ids
        filters = {
            "field": "meta.document_id",
            "operator": "in",
            "value": [str(doc_id) for doc_id in document_ids],
        }

        # Convert chat history to Haystack format
        haystack_history = [
            HaystackChatMessage.from_user(msg["content"])
            if msg["role"] == "user"
            else HaystackChatMessage.from_assistant(msg["content"])
            for msg in chat_history
        ]

        # Run RAG pipeline
        result = self.rag_pipeline.run(
            {
                "embedder": {"text": question},
                "retriever": {"filters": filters},
                "prompt_builder": {
                    "question": question,
                    "chat_history": haystack_history,
                    "current_date": datetime.now().strftime("%B %d, %Y"),
                },
            },
            include_outputs_from={"retriever"},
        )

        # Extract response and sources
        response = result["llm"]["replies"][0]
        documents = result.get("retriever", {}).get("documents", [])

        sources = []
        for doc in documents:
            filename = doc.meta.get("filename", "Unknown")
            sources.append(f"{filename} (score: {doc.score:.3f})")

        confidence_score = self._calculate_confidence(question, documents)

        return {
            "answer": response,
            "sources": sources,
            "retrieved_documents": len(documents),
            "confidence_score": confidence_score,
        }

    def _calculate_confidence(
        self, question: str, documents: List[HaystackDocument]
    ) -> float:
        """
        Calculate confidence score based on document relevance and context.

        This method is used to calculate the confidence score based on the document relevance and context.

        Args:
            question: The question to calculate the confidence score for.
            documents: The documents to calculate the confidence score for.

        Returns:
            float: The confidence score.
        """
        # Simple scoring:
        # - 100% if question is in context
        # - 0% if not in context
        # - 50% if partially relevant
        # This can be improved with more sophisticated scoring logic
        if any(question in doc.content for doc in documents):
            return 1.0
