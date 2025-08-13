from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import file_router, chat_router
from src.core.config import Settings
from src.db.database import init_db
from src.db.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This is the lifespan of the application.
    """
    # Startup
    await init_db()
    await redis_client.connect()

    yield

    # Shutdown
    await redis_client.disconnect()


app = FastAPI(
    title="AI Chatbot API",
    description="A RAG-based chatbot for PDF documents using Haystack",
    version="1.0.0",
    lifespan=lifespan,
)

settings = Settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(file_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/health")
async def health_check():
    """
    This is a health check endpoint.
    """
    return {"status": "healthy"}
