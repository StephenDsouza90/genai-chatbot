import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from haystack import Pipeline, component
from haystack.components.embedders import AzureOpenAITextEmbedder, AzureOpenAIDocumentEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.generators import AzureOpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.dataclasses import Document as HaystackDocument, ChatMessage as HaystackChatMessage
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.utils import Secret
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.retrievers.pgvector.embedding_retriever import PgvectorEmbeddingRetriever

from src.core.config import Settings


@component
class MetadataAdder:
    """Haystack component that adds provided metadata to each Document."""

    @component.output_types(documents=List[HaystackDocument])
    def run(
        self,
        documents: List[HaystackDocument],
        meta: Dict[str, Any] | None = None,
    ) -> Dict[str, List[HaystackDocument]]:
        if meta:
            for doc in documents:
                # Ensure meta exists and update
                if doc.meta is None:
                    doc.meta = {}
                doc.meta.update(meta)
        return {"documents": documents}


class HaystackService:
    def __init__(self):
        self.settings = Settings()

        # Prepare a psycopg-compatible connection string for Pgvector
        pg_conn_str = self.settings.DATABASE_URL or ""
        if pg_conn_str.startswith("postgresql+asyncpg://"):
            pg_conn_str = pg_conn_str.replace("postgresql+asyncpg://", "postgresql://", 1)

        # Initialize PGVector document store (ensure dimension matches embedder)
        self.document_store = PgvectorDocumentStore(
            connection_string=Secret.from_token(pg_conn_str),
            table_name="haystack_documents",
            embedding_dimension=self.settings.EMBEDDING_DIMENSION,
            vector_function="cosine_similarity",
            # recreate_table=True,
        )
        
        # Initialize pipelines
        self._init_indexing_pipeline()
        self._init_rag_pipeline()
    
    def _init_indexing_pipeline(self):
        """Initialize the document indexing pipeline"""
        self.indexing_pipeline = Pipeline()
        
        # Add components
        self.indexing_pipeline.add_component("converter", PyPDFToDocument())
        self.indexing_pipeline.add_component(
            "splitter", 
            DocumentSplitter(split_by="word", split_length=200, split_overlap=50)
        )
        self.indexing_pipeline.add_component("meta_adder", MetadataAdder())
        self.indexing_pipeline.add_component(
            "embedder", 
            AzureOpenAIDocumentEmbedder(
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
                api_version=self.settings.API_VERSION,
                azure_deployment=self.settings.EMBEDDING_MODEL,
                api_key=Secret.from_token(self.settings.OPENAI_API_KEY)
            )
        )
        self.indexing_pipeline.add_component("writer", DocumentWriter(document_store=self.document_store))
        
        # Connect components
        self.indexing_pipeline.connect("converter", "splitter")
        self.indexing_pipeline.connect("splitter", "meta_adder.documents")
        self.indexing_pipeline.connect("meta_adder", "embedder")
        self.indexing_pipeline.connect("embedder", "writer")
    
    def _init_rag_pipeline(self):
        """Initialize the RAG pipeline"""
        self.rag_pipeline = Pipeline()
        
        # Add components
        self.rag_pipeline.add_component(
            "embedder",
            AzureOpenAITextEmbedder(
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
                api_version=self.settings.API_VERSION,
                azure_deployment=self.settings.EMBEDDING_MODEL,
                api_key=Secret.from_token(self.settings.OPENAI_API_KEY)
            )
        )
        self.rag_pipeline.add_component(
            "retriever",
            PgvectorEmbeddingRetriever(document_store=self.document_store, top_k=5)
        )
        self.rag_pipeline.add_component("prompt_builder", PromptBuilder(template=self._get_prompt_template()))
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
                }
            )
        )
        
        # Connect components
        self.rag_pipeline.connect("embedder.embedding", "retriever.query_embedding")
        self.rag_pipeline.connect("retriever", "prompt_builder.documents")
        self.rag_pipeline.connect("prompt_builder", "llm")
    
    def _get_prompt_template(self) -> str:
        """Get the prompt template for RAG"""
        return """
        You are a helpful assistant that answers questions based on the provided context and chat history.
        
        IMPORTANT RULES:
        1. Use information from the context documents to answer questions.
        2. Use the chat history to understand references (like "he", "she", "it", "they") and maintain conversation continuity.
        3. When pronouns or unclear references are used, look at the chat history to identify who or what is being discussed.
        4. If the context doesn't contain enough information to answer the question, say "I cannot answer this question based on the provided context" with giving a reason.
        5. Do not make assumptions beyond what can be reasonably inferred from the context and chat history.
        6. If you're unsure about any detail, acknowledge the uncertainty
        7. When calculating time periods or durations, use the current date: {{ current_date }}. Always calculate durations from the start date to the current date, not from any other reference point.
        8. For any date-based calculations (experience, project duration, time periods, etc.), use the current date ({{ current_date }}) as the end point, not any other reference date.
        9. You can perform future date calculations if given a specific future date, as long as you're only doing mathematical date arithmetic from known start dates.
        
        Context Documents:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}
        
        Chat History:
        {% for message in chat_history %}
            {{ message.role }}: {{ message.content }}
        {% endfor %}
        
        Question: {{ question }}
        
        Answer based on the context documents above, using the chat history to understand references and maintain conversation flow:
        """
    
    async def process_document(self, file_content: bytes, filename: str, document_id: UUID) -> Dict[str, Any]:
        """Process a document using Haystack pipeline"""
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
                "success": True
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    async def query(self, question: str, document_ids: List[UUID], chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Query documents using RAG pipeline"""
        # Filter documents by document_ids
        filters = {
            "field": "meta.document_id",
            "operator": "in",
            "value": [str(doc_id) for doc_id in document_ids]
        }
        
        # Convert chat history to Haystack format
        haystack_history = [
            HaystackChatMessage.from_user(msg["content"]) if msg["role"] == "user" 
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
                    "current_date": datetime.now().strftime("%B %d, %Y")
                }
            },
            include_outputs_from={"retriever"}
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
            "confidence_score": confidence_score
        }

    def _calculate_confidence(self, question: str, documents: List[HaystackDocument]) -> float:
        """Calculate confidence score based on document relevance and context"""
        # Simple scoring:
        # - 100% if question is in context
        # - 0% if not in context
        # - 50% if partially relevant
        # This can be improved with more sophisticated scoring logic
        if any(question in doc.content for doc in documents):
            return 1.0