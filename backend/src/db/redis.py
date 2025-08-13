import json
from typing import Optional, List, Any

import redis.asyncio as redis

from src.core.config import Settings


class RedisClient:
    def __init__(self):
        self.settings = Settings()
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                db=self.settings.REDIS_DB,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            print("✅ Connected to Redis successfully")
            
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a JSON value in Redis with optional TTL (time to live)"""
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
        """Get a JSON value from Redis"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False
    
    async def list_push(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Push value to Redis list"""
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
        """Get all values from Redis list"""
        try:
            values = await self.redis.lrange(key, 0, -1)
            return [json.loads(v) for v in reversed(values)]  # Reverse to maintain order
        except Exception as e:
            print(f"Redis list get error: {e}")
            return []
    
    async def list_trim(self, key: str, max_length: int) -> bool:
        """Trim Redis list to max length (keep most recent)"""
        try:
            await self.redis.ltrim(key, 0, max_length - 1)
            return True
        except Exception as e:
            print(f"Redis list trim error: {e}")
            return False
    
    async def keys(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern"""
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            print(f"Redis keys error: {e}")
            return []


# Global Redis client instance to be reused across the app
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """FastAPI dependency to provide the shared Redis client"""
    return redis_client
