# NEXORA

NEXORA is an AI-powered labour-market intelligence and skill-alignment platform.

## Architecture

The platform consists of:
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, Pydantic, Uvicorn
- **Database:** Supabase PostgreSQL (Structured data)
- **File Storage:** Cloudflare R2 (Documents, Resumes)
- **Vector DB:** Qdrant (Embeddings for AI/RAG)
- **Cache/Realtime:** Redis
- **AI Orchestration:** LangGraph & Gemini

## Repository Structure

- `/frontend` - React application
- `/backend` - FastAPI application
- `/agents` - AI agents and LangGraph workflows
- `/data-pipeline` - Data ingestion and processing
- `/infrastructure` - Docker, DB configurations, etc.
- `/docs` - Documentation

## Local Setup

### Prerequisites
- Docker & Docker Compose
- Node.js (for frontend development)
- Python 3.11+ (for backend development)

### Environment Configuration
1. Copy `.env.example` to `.env` in the root directory.
2. Fill in the required environment variables.

### Running with Docker Compose
```bash
docker compose up --build
```
This will start the frontend, backend, Redis, and Qdrant.

## Testing
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm run build` (For build testing)

## Future Roadmap
- Module 1: Auth & User Profiles
- Module 2: Labour Market Intelligence
- Module 3: Skill Sync & RAG
- Module 4: Assessment & AI Interviews
