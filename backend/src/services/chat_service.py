from typing import List
from uuid import UUID

from src.models.schemas import ChatResponse
from src.services.haystack_service import HaystackService
from src.services.session_service import SessionService


class ChatService:
    def __init__(
        self, haystack_service: HaystackService, session_service: SessionService
    ):
        self.haystack_service = haystack_service
        self.session_service = session_service

    async def chat(
        self, question: str, document_ids: List[UUID], session_id: str = None
    ) -> ChatResponse:
        """Process chat question and return response with proper session management"""

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
