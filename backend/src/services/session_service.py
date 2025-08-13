import uuid
from typing import List, Dict, Optional
from datetime import datetime

from src.db.redis import RedisClient
from src.models.schemas import CreateSessionResponse
from src.core.config import Settings
from src.core.exceptions import SessionNotFoundError


class SessionService:
    def __init__(self, redis_client: RedisClient):
        self.settings = Settings()
        self.redis = redis_client
        self.session_prefix = "chat_session:"
        self.session_ttl = self.settings.SESSION_TIMEOUT
        self.max_messages = self.settings.MAX_MESSAGES_PER_SESSION

    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{self.session_prefix}{session_id}"

    async def create_session(self) -> CreateSessionResponse:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session_key = self._get_session_key(session_id)

        # Initialize empty session with TTL
        session_data = {
            "session_id": session_id,
            "messages": [],
            "created_at": str(
                int(datetime.now().timestamp() * 1000)
            ),  # Unix timestamp in milliseconds
        }

        success = await self.redis.set_json(session_key, session_data, self.session_ttl)

        if not success:
            raise Exception("Failed to create session in Redis")

        return CreateSessionResponse(
            session_id=session_id, message="Chat session created successfully"
        )

    async def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get chat history for a session"""
        session_key = self._get_session_key(session_id)

        session_data = await self.redis.get_json(session_key)

        if not session_data:
            raise SessionNotFoundError(f"Session {session_id} not found or expired")

        return session_data.get("messages", [])

    async def add_messages_to_session(
        self, session_id: str, messages: List[Dict[str, str]]
    ):
        """Add messages to session history"""
        session_key = self._get_session_key(session_id)

        # Get existing session data
        session_data = await self.redis.get_json(session_key)

        if not session_data:
            raise SessionNotFoundError(f"Session {session_id} not found or expired")

        # Add new messages
        if "messages" not in session_data:
            session_data["messages"] = []

        session_data["messages"].extend(messages)

        # Keep only the most recent messages
        if len(session_data["messages"]) > self.max_messages:
            session_data["messages"] = session_data["messages"][-self.max_messages :]

        # Update session data with renewed TTL
        success = await self.redis.set_json(session_key, session_data, self.session_ttl)

        if not success:
            raise Exception("Failed to update session in Redis")

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        session_key = self._get_session_key(session_id)
        return await self.redis.delete(session_key)

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        session_key = self._get_session_key(session_id)
        return await self.redis.exists(session_key)

    async def extend_session_ttl(self, session_id: str) -> bool:
        """Extend session TTL (refresh expiration)"""
        session_key = self._get_session_key(session_id)
        return await self.redis.expire(session_key, self.session_ttl)

    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session metadata (for debugging/monitoring)"""
        session_key = self._get_session_key(session_id)

        session_data = await self.redis.get_json(session_key)

        if not session_data:
            return None

        return {
            "session_id": session_id,
            "message_count": len(session_data.get("messages", [])),
            "created_at": session_data.get("created_at"),
            "ttl_remaining": await self.redis.redis.ttl(session_key)
            if self.redis.redis
            else -1,
        }

    async def get_all_sessions(self) -> List[Dict]:
        """Get all chat sessions"""
        try:
            # Get all keys with session prefix
            session_keys = await self.redis.keys(f"{self.session_prefix}*")
            sessions = []

            for key in session_keys:
                session_id = key.replace(self.session_prefix, "")
                session_data = await self.redis.get_json(key)

                if session_data:
                    session_info = {
                        "session_id": session_id,
                        "message_count": len(session_data.get("messages", [])),
                        "created_at": session_data.get("created_at"),
                        "ttl_remaining": await self.redis.redis.ttl(key)
                        if self.redis.redis
                        else -1,
                        "last_message": session_data.get("messages", [])[-1]
                        if session_data.get("messages")
                        else None,
                    }
                    sessions.append(session_info)

            # Sort by creation time (newest first)
            sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return sessions

        except Exception as e:
            print(f"Error getting all sessions: {e}")
            return []
