from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import List, Optional


class FileMetadata(BaseModel):
    id: UUID
    filename: str
    upload_date: datetime
    file_size: int
    chunk_count: int

    class Config:
        """
        This is used to convert the model to a dictionary when it is returned in a response.
        """
        from_attributes = True


class ChatMessage(BaseModel):
    question: str
    document_ids: List[UUID]
    session_id: Optional[str] = None  # Optional for backward compatibility


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    session_id: str


class UploadResponse(BaseModel):
    message: str
    file_id: UUID
    filename: str


class CreateSessionResponse(BaseModel):
    session_id: str
    message: str