# Architecture

NEXORA Architecture Principles:
- **Frontend / Backend Separation:** The frontend is a React application communicating via REST APIs (and WebSockets in the future) with the Python FastAPI backend.
- **Service Boundaries:** External integrations (Firebase, Supabase, Cloudflare R2, Qdrant) must be abstracted behind clean service boundaries.
- **Data Storage:**
  - Supabase PostgreSQL: Relational structured data.
  - Cloudflare R2: Unstructured files, resumes.
  - Qdrant: Vector embeddings for AI retrieval.
  - Redis: Cache and realtime pub-sub coordination.
- **AI Architecture:** AI agents will be orchestrated via LangGraph, interacting with Gemini, and utilizing Qdrant for RAG.
