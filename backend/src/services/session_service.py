import uuid
from typing import List, Dict, Optional
from datetime import datetime

from src.db.redis import RedisClient
from src.models.schemas import CreateSessionResponse
from src.core.config import Settings
from src.core.exceptions import SessionNotFoundError


class SessionService:
    """
    Service for managing chat sessions.

    This service is responsible for creating, retrieving, and deleting chat sessions.
    It also provides methods for adding messages to sessions and extending session TTL.

    Attributes:
        redis_client: The Redis client for storing session data.
        settings: The application settings.
        session_prefix: The prefix for the Redis keys.
        session_ttl: The TTL for the sessions.
        max_messages: The maximum number of messages per session.
    """
    def __init__(self, redis_client: RedisClient):
        """
        Initialize the SessionService with the necessary Redis client.

        Args:
            redis_client: The Redis client for storing session data.
        """
        self.settings = Settings()
        self.redis = redis_client
        self.session_prefix = "chat_session:"
        self.session_ttl = self.settings.SESSION_TIMEOUT
        self.max_messages = self.settings.MAX_MESSAGES_PER_SESSION

    def _get_session_key(self, session_id: str) -> str:
        """
        Get Redis key for session.

        This method is used to get the Redis key for a session.

        Args:
            session_id: The ID of the session.

        Returns:
            str: The Redis key for the session.
        """
        return f"{self.session_prefix}{session_id}"

    async def create_session(self) -> CreateSessionResponse:
        """
        Create a new chat session.

        This method is used to create a new chat session.
        It generates a new session ID and initializes the session data.

        Returns:
            CreateSessionResponse: The response containing the session ID and message.

        Raises:
            Exception: If there is an error creating the session.
        """
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
        """
        Get chat history for a session.

        This method is used to get the chat history for a session.
        It retrieves the session data from Redis and returns the messages.

        Args:
            session_id: The ID of the session.

        Returns:
            List[Dict[str, str]]: The chat history for the session.

        Raises:
            SessionNotFoundError: If the session is not found or expired.
        """
        session_key = self._get_session_key(session_id)

        session_data = await self.redis.get_json(session_key)

        if not session_data:
            raise SessionNotFoundError(f"Session {session_id} not found or expired")

        return session_data.get("messages", [])

    async def add_messages_to_session(
        self, session_id: str, messages: List[Dict[str, str]]
    ):
        """
        Add messages to session history.

        This method is used to add messages to the session history.
        It retrieves the session data from Redis and adds the messages to the session.

        Args:
            session_id: The ID of the session.
            messages: The messages to add to the session.

        Returns:
            None
        """
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
        """
        Delete a chat session.

        This method is used to delete a chat session.
        It deletes the session data from Redis.

        Args:
            session_id: The ID of the session.

        Returns:
            bool: True if the session was deleted, False otherwise.
        """
        session_key = self._get_session_key(session_id)
        return await self.redis.delete(session_key)

    async def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists.

        This method is used to check if a session exists.
        It checks if the session data exists in Redis.

        Args:
            session_id: The ID of the session.

        Returns:
            bool: True if the session exists, False otherwise.
        """
        session_key = self._get_session_key(session_id)
        return await self.redis.exists(session_key)

    async def extend_session_ttl(self, session_id: str) -> bool:
        """Extend session TTL (refresh expiration).

        This method is used to extend the TTL of a session.
        It refreshes the expiration time of the session data in Redis.

        Args:
            session_id: The ID of the session.

        Returns:
            bool: True if the session TTL was extended, False otherwise.
        """
        session_key = self._get_session_key(session_id)
        return await self.redis.expire(session_key, self.session_ttl)

    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session metadata (for debugging/monitoring).

        This method is used to get the metadata for a session.
        It retrieves the session data from Redis and returns the metadata.

        Args:
            session_id: The ID of the session.

        Returns:
            Optional[Dict]: The metadata for the session.
        """

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
        """
        Get all chat sessions.

        This method is used to get all the sessions in Redis.
        It retrieves all the session data from Redis and returns the metadata.

        Returns:
            List[Dict]: The metadata for all the sessions.

        Raises:
            Exception: If there is an error getting the sessions.
        """

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
