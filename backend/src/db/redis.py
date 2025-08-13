import json
from typing import Optional, List, Any

import redis.asyncio as redis

from src.core.config import Settings


class RedisClient:
    """
    Redis client for interacting with Redis.

    This class is used to interact with Redis.
    """

    def __init__(self):
        """
        Initialize the Redis client.

        This method initializes the Redis client with the necessary settings.
        It also creates a connection to Redis.
        """
        self.settings = Settings()
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """
        Initialize Redis connection.

        This method initializes the Redis connection with the necessary settings.
        It also tests the connection to Redis.

        Returns:
            None

        Raises:
            Exception: If there is an error connecting to Redis.
        """

        try:
            self.redis = redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                db=self.settings.REDIS_DB,
                decode_responses=True,
            )

            # Test connection
            await self.redis.ping()
            print("✅ Connected to Redis successfully")

        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """
        Close Redis connection.

        This method closes the Redis connection.

        Returns:
            None

        Raises:
            Exception: If there is an error closing the Redis connection.
        """

        if self.redis:
            await self.redis.close()

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a JSON value in Redis with optional TTL (time to live).

        This method sets a JSON value in Redis with an optional TTL.

        Args:
            key: The key to set the JSON value in.
            value: The value to set in Redis.
            ttl: The TTL for the key.

        Returns:
            bool: True if the value was set, False otherwise.

        Raises:
            Exception: If there is an error setting the JSON value in Redis.
        """

        try:
            json_value = json.dumps(value, default=str)
            if ttl:
                return await self.redis.setex(key, ttl, json_value)
            else:
                return await self.redis.set(key, json_value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get a JSON value from Redis.

        This method gets a JSON value from Redis.

        Args:
            key: The key to get the JSON value from.

        Returns:
            Optional[Any]: The JSON value from Redis.
        """

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.

        This method deletes a key from Redis.

        Args:
            key: The key to delete from Redis.

        Returns:
            bool: True if the key was deleted, False otherwise.

        Raises:
            Exception: If there is an error deleting the key from Redis.
        """

        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        This method checks if a key exists in Redis.

        Args:
            key: The key to check if it exists in Redis.

        Returns:
            bool: True if the key exists, False otherwise.

        Raises:
            Exception: If there is an error checking if the key exists in Redis.
        """

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set TTL for existing key.

        This method sets the TTL for an existing key in Redis.

        Args:
            key: The key to set the TTL for.
            ttl: The TTL for the key.

        Returns:
            bool: True if the TTL was set, False otherwise.

        Raises:
            Exception: If there is an error setting the TTL for the key in Redis.
        """

        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False

    async def list_push(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Push value to Redis list.

        This method pushes a value to a Redis list.

        Args:
            key: The key to push the value to.
            value: The value to push to the Redis list.
            ttl: The TTL for the key.

        Returns:
            bool: True if the value was pushed, False otherwise.

        Raises:
            Exception: If there is an error pushing the value to the Redis list.
        """

        try:
            json_value = json.dumps(value, default=str)
            await self.redis.lpush(key, json_value)

            if ttl:
                await self.redis.expire(key, ttl)

            return True
        except Exception as e:
            print(f"Redis list push error: {e}")
            return False

    async def list_get_all(self, key: str) -> List[Any]:
        """
        Get all values from Redis list.

        This method gets all the values from a Redis list.

        Args:
            key: The key to get the values from.

        Returns:
            List[Any]: The values from the Redis list.

        Raises:
            Exception: If there is an error getting the values from the Redis list.
        """

        try:
            values = await self.redis.lrange(key, 0, -1)
            return [
                json.loads(v) for v in reversed(values)
            ]  # Reverse to maintain order
        except Exception as e:
            print(f"Redis list get error: {e}")
            return []

    async def list_trim(self, key: str, max_length: int) -> bool:
        """
        Trim Redis list to max length (keep most recent).

        This method trims a Redis list to a maximum length.

        Args:
            key: The key to trim the Redis list from.
            max_length: The maximum length of the Redis list.

        Returns:
            bool: True if the list was trimmed, False otherwise.

        Raises:
            Exception: If there is an error trimming the Redis list.
        """

        try:
            await self.redis.ltrim(key, 0, max_length - 1)
            return True
        except Exception as e:
            print(f"Redis list trim error: {e}")
            return False

    async def keys(self, pattern: str) -> List[str]:
        """
        Get all keys matching a pattern.

        This method gets all the keys that match a pattern in Redis.

        Args:
            pattern: The pattern to match the keys.

        Returns:
            List[str]: The keys that match the pattern.

        Raises:
            Exception: If there is an error getting the keys from Redis.
        """

        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            print(f"Redis keys error: {e}")
            return []


# Global Redis client instance to be reused across the app
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    FastAPI dependency to provide the shared Redis client.

    This function is used to provide the shared Redis client to the FastAPI app.
    """

    return redis_client
