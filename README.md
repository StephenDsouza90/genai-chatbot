# AI Document Chatbot

A modern, full-stack AI chatbot application that enables users to upload PDF documents and engage in intelligent conversations about their content using Retrieval-Augmented Generation (RAG) technology.

## 🚀 Features

- **Document Processing**: Upload and process PDF documents with automatic text extraction and chunking
- **Intelligent Chat**: Ask questions about your documents and receive context-aware AI responses
- **Session Management**: Maintain conversation context across multiple chat sessions
- **File Management**: Organize and select documents for context-aware conversations
- **Responsive Design**: Modern, mobile-friendly interface with drag-and-drop file uploads
- **Real-time Processing**: Fast document indexing and retrieval using vector embeddings

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: Haystack, Azure OpenAI (GPT-4o, text-embedding-ada-002)
- **Database**: PostgreSQL with pgvector extension for vector storage
- **Caching**: Redis for session management
- **Document Processing**: PyPDF4 for PDF text extraction
- **Vector Embeddings**: Azure OpenAI text-embedding-ada-002 (1536 dimensions)

### Frontend
- **Framework**: React with modern hooks
- **State Management**: Zustand for lightweight state management
- **UI Components**: Custom components with responsive design
- **File Handling**: React Dropzone for drag-and-drop file uploads
- **Styling**: CSS-in-JS with modern design patterns
- **HTTP Client**: Axios for API communication

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local development
- **Web Server**: Nginx for frontend serving
- **Process Management**: Uvicorn ASGI server for backend

## 📋 Prerequisites

- Docker and Docker Compose
- Azure OpenAI API access (for AI models)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/StephenDsouza90/genai-chatbot.git
cd genai-chatbot
```

### 2. Environment Configuration
Create a `.env` file in the root directory with your Azure OpenAI credentials:
```bash
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
OPENAI_API_KEY=your_openai_api_key
```

### 3. Launch with Docker Compose
```bash
docker-compose up --build -d
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: localhost:5432
- **Redis**: localhost:6379

### 4. Health Check
Verify all services are running:
```bash
curl http://localhost:8000/health
```

## 📚 API Endpoints

### Document Management
- `POST /api/upload-file` - Upload and process PDF documents
- `GET /api/files` - Retrieve list of uploaded documents

### Chat Operations
- `POST /api/create-session` - Create new chat session
- `POST /api/chat` - Send message and receive AI response
- `DELETE /api/session/{session_id}` - Delete chat session
- `GET /api/session/{session_id}/info` - Get session information

## 🏗️ Architecture

### Backend Services
- **Document Service**: Handles PDF processing, text extraction, and vector storage
- **Chat Service**: Manages conversation flow and AI response generation
- **Session Service**: Maintains chat session state and conversation history
- **Haystack Service**: Orchestrates RAG pipeline with document retrieval and generation

### Data Flow
1. **Document Upload**: PDF → Text Extraction → Chunking → Vector Embeddings → Storage
2. **Chat Processing**: User Question → Vector Search → Context Retrieval → AI Generation → Response
3. **Session Management**: Redis-based conversation history and context preservation

### Database Schema
- **Documents**: File metadata, content chunks, and vector embeddings
- **Sessions**: Chat session information and message history
- **Vector Storage**: pgvector tables for similarity search

## 🔧 Development

### Local Development Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm start
```

### Code Structure
```
├── backend/
│   ├── src/
│   │   ├── api/          # FastAPI route definitions
│   │   ├── core/         # Configuration and settings
│   │   ├── db/           # Database connections and models
│   │   ├── models/       # Data models and schemas
│   │   └── services/     # Business logic services
│   ├── main.py           # FastAPI application entry point
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   ├── store/        # State management
│   │   └── utils/        # Utility functions
│   └── package.json      # Node.js dependencies
└── docker-compose.yml    # Service orchestration
```

## 🐳 Docker Configuration

### Service Dependencies
- **Redis**: Session storage and caching
- **PostgreSQL**: Document and metadata storage
- **Backend**: FastAPI application with AI services
- **Frontend**: React application served via Nginx

### Volume Mounts
- `./uploads`: Document storage directory
- `postgres_data`: PostgreSQL data persistence
- `redis_data`: Redis data persistence



## 📱 User Interface

### Key Components
- **File Upload**: Drag-and-drop interface with file validation
- **Document List**: Checkbox selection for context-aware conversations
- **Chat Interface**: Real-time messaging with markdown support
- **Session Management**: Persistent conversation history
- **Responsive Design**: Mobile-optimized layout

### User Experience
- Intuitive file management
- Real-time chat interactions
- Context-aware AI responses
- Session persistence across browser sessions
- Mobile-responsive design
