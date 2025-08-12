import uuid

from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    file_size = Column(Integer, nullable=False)
    chunk_count = Column(Integer, default=0)


# class DocumentChunk(Base):
#     __tablename__ = "document_chunks"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     document_id = Column(UUID(as_uuid=True), nullable=False)
#     content = Column(Text, nullable=False)
#     chunk_index = Column(Integer, nullable=False)
#     metadata = Column(JSON, default={})  # Store additional metadata
