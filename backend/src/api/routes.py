from typing import List, Dict

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.redis import get_redis, RedisClient
from src.models.schemas import (
    FileMetadata,
    ChatMessage,
    ChatResponse,
    UploadResponse,
    CreateSessionResponse,
)
from src.services.document_service import DocumentService
from src.services.chat_service import ChatService
from src.services.session_service import SessionService
from src.services.haystack_service import HaystackService

# Create routers
file_router = APIRouter(tags=["files"])
chat_router = APIRouter(tags=["chat"])

# Initialize services
haystack_service = HaystackService()


def get_services(redis_client: RedisClient = Depends(get_redis)):
    """Dependency to get services with Redis"""
    session_service = SessionService(redis_client)
    document_service = DocumentService(haystack_service)
    chat_service = ChatService(haystack_service, session_service)
    return document_service, chat_service, session_service


@file_router.post("/upload-file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    services=Depends(get_services),
):
    """Upload a PDF file and process it using Haystack"""
    try:
        document_service, _, _ = services
        file_metadata = await document_service.upload_file(file, db)
        return UploadResponse(
            message="File uploaded and processed successfully",
            file_id=file_metadata.id,
            filename=file_metadata.filename,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@file_router.get("/files", response_model=List[FileMetadata])
async def get_files(db: AsyncSession = Depends(get_db), services=Depends(get_services)):
    """Get list of all uploaded files"""
    try:
        document_service, _, _ = services
        return await document_service.get_all_files(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/create-session", response_model=CreateSessionResponse)
async def create_chat_session(services=Depends(get_services)):
    """Create a new chat session"""
    try:
        _, _, session_service = services
        return await session_service.create_session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, services=Depends(get_services)):
    """Process chat message and return AI response with session management"""
    try:
        _, chat_service, _ = services
        return await chat_service.chat(
            message.question, message.document_ids, message.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.delete("/session/{session_id}")
async def delete_session(session_id: str, services=Depends(get_services)):
    """Delete a chat session"""
    try:
        _, _, session_service = services
        success = await session_service.delete_session(session_id)
        if success:
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/session/{session_id}/info")
async def get_session_info(session_id: str, services=Depends(get_services)):
    """Get session information (for debugging/monitoring)"""
    try:
        _, _, session_service = services
        info = await session_service.get_session_info(session_id)
        if info:
            return info
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/sessions", response_model=List[Dict])
async def get_all_sessions(services=Depends(get_services)):
    """Get list of all chat sessions"""
    try:
        _, _, session_service = services
        sessions = await session_service.get_all_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/session/{session_id}/history")
async def get_session_history(session_id: str, services=Depends(get_services)):
    """Get chat history for a specific session"""
    try:
        _, _, session_service = services
        history = await session_service.get_session_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Session not found")
        raise HTTPException(status_code=500, detail=str(e))
