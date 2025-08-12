import os
from typing import List
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.database import Document
from src.models.schemas import FileMetadata
from src.core.config import Settings
from src.core.exceptions import InvalidFileTypeError, FileTooLargeError
from src.services.haystack_service import HaystackService


class DocumentService:
    def __init__(self, haystack_service: HaystackService):
        self.settings = Settings()
        self.haystack_service = haystack_service
        
    async def upload_file(self, file: UploadFile, db: AsyncSession) -> FileMetadata:
        """Upload and process a PDF file using Haystack"""
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise InvalidFileTypeError("Only PDF files are allowed")
        
        # Read file content
        content = await file.read()
        if len(content) > self.settings.MAX_FILE_SIZE:
            raise FileTooLargeError(f"File size exceeds {self.settings.MAX_FILE_SIZE} bytes")
        
        # Create document record
        document = Document(
            filename=file.filename,
            file_size=len(content)
        )
        db.add(document)
        await db.flush()  # Get the ID
        
        # Process document with Haystack
        result = await self.haystack_service.process_document(
            content, file.filename, document.id
        )
        
        document.chunk_count = result.get("documents_processed", 0)
        await db.commit()
        
        return FileMetadata(
            id=document.id,
            filename=document.filename,
            upload_date=document.upload_date,
            file_size=document.file_size,
            chunk_count=document.chunk_count
        )
    
    async def get_all_files(self, db: AsyncSession) -> List[FileMetadata]:
        """Get all uploaded files"""
        result = await db.execute(select(Document))
        documents = result.scalars().all()
        
        return [
            FileMetadata(
                id=doc.id,
                filename=doc.filename,
                upload_date=doc.upload_date,
                file_size=doc.file_size,
                chunk_count=doc.chunk_count
            )
            for doc in documents
        ]