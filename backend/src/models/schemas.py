from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import List, Optional


class FileMetadata(BaseModel):
    """
    Model for storing file metadata.

    This model is used to store the metadata for the uploaded files.

    Attributes:
        id: The ID of the file.
        filename: The name of the file.
        upload_date: The date and time the file was uploaded.
        file_size: The size of the file.
        chunk_count: The number of chunks in the file.
    """

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
    """
    Model for storing chat messages.

    This model is used to store the chat messages.

    Attributes:
        question: The question to be answered.
        document_ids: The IDs of the documents to be used as context for the question.
        session_id: The ID of the session.
    """

    question: str
    document_ids: List[UUID]
    session_id: Optional[str] = None  # Optional for backward compatibility


class ChatResponse(BaseModel):
    """
    Model for storing chat responses.

    This model is used to store the chat responses.

    Attributes:
        answer: The answer to the question.
        sources: The sources used to answer the question.
        session_id: The ID of the session.
    """

    answer: str
    sources: Optional[List[str]] = None
    session_id: str


class UploadResponse(BaseModel):
    """
    Model for storing upload responses.

    This model is used to store the upload responses.

    Attributes:
        message: The message to be displayed to the user.
        file_id: The ID of the file.
        filename: The name of the file.
    """

    message: str
    file_id: UUID
    filename: str


class CreateSessionResponse(BaseModel):
    """
    Model for storing create session responses.

    This model is used to store the create session responses.

    Attributes:
        session_id: The ID of the session.
        message: The message to be displayed to the user.
    """

    session_id: str
    message: str
