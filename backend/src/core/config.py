import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application.

    This class is used to store the settings for the application.
    """

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", ""))
    REDIS_DB: int = 0

    # LLM
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    API_VERSION: str = "2023-12-01-preview"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    CHAT_MODEL: str = "gpt-4o"
    EMBEDDING_DIMENSION: int = 1536

    # Control Parameters
    TEMPERATURE: float = 0.1  # Lower temperature means more deterministic responses
    MAX_TOKENS: int = 2000  # Maximum number of tokens to generate
    TOP_P: float = 0.9  # Nucleus sampling parameter
    PRESENCE_PENALTY: float = 0.1  # Encourage covering all relevant points
    FREQUENCY_PENALTY: float = 0.1  # Reduce repetition

    # Retrieval
    TOP_K: int = 25  # Number of documents to retrieve

    # Split documents
    SPLIT_BY: str = "word"  # How to split the documents
    SPLIT_LENGTH: int = 800  # Maximum number of tokens per chunk
    SPLIT_OVERLAP: int = 200  # Overlap between chunks

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:3000"]

    # File upload
    MAX_FILE_SIZE: int = 52428800
    UPLOAD_DIR: str = "uploads"

    # Session management
    SESSION_TIMEOUT: int = 3600  # 1 hour in seconds
    MAX_MESSAGES_PER_SESSION: int = 20  # Max messages to keep in session
