from typing import List
from uuid import UUID

from src.models.schemas import ChatResponse
from src.services.haystack_service import HaystackService
from src.services.session_service import SessionService


class ChatService:
    """
    Service for handling chat interactions with the AI.

    This service orchestrates the process of answering user questions using the Haystack service.
    It manages the chat session lifecycle, including creating new sessions,
    retrieving chat history, and processing new questions. The user's question is sent to the
    Haystack service to retrieve relevant documents and context, which is then passed to
    the AI model to generate a response. The response is then stored in the session and returned
    to the user.

    Attributes:
        haystack_service: The Haystack service for document retrieval and context generation.
        session_service: The session service for managing chat sessions and history.

    Methods:
        chat: Process a user question and return a response with proper session management.
    """
    def __init__(
        self, haystack_service: HaystackService, session_service: SessionService
    ):
        """
        Initialize the ChatService with the necessary services.

        Args:
            haystack_service: The Haystack service for document retrieval and context generation.
            session_service: The session service for managing chat sessions and history.
        """
        self.haystack_service = haystack_service
        self.session_service = session_service

    async def chat(
        self, question: str, document_ids: List[UUID], session_id: str = None
    ) -> ChatResponse:
        """
        Process a user question and return a response with proper session management.

        Args:
            question: The user's question to be answered.
            document_ids: The IDs of the documents to be used as context for the question.
            session_id: The ID of the chat session to be used. If not provided, a new session will be created.

        Returns:
            ChatResponse: A response containing the answer, sources, and session ID.

        Raises:
            Exception: If there is an error processing the question.
        """

        # Create session if not provided
        if not session_id:
            session_response = await self.session_service.create_session()
            session_id = session_response.session_id

        # Get chat history
        try:
            chat_history = await self.session_service.get_session_history(session_id)
        except Exception:
            # If session doesn't exist or expired, create a new one
            session_response = await self.session_service.create_session()
            session_id = session_response.session_id
            chat_history = []

        # Query using Haystack
        result = await self.haystack_service.query(question, document_ids, chat_history)

        # Update session with new messages
        new_messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": result["answer"]},
        ]
        await self.session_service.add_messages_to_session(session_id, new_messages)

        return ChatResponse(
            answer=result["answer"], sources=result["sources"], session_id=session_id
        )
