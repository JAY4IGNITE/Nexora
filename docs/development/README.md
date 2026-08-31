# Development Guide

## Local Setup

### Backend (Python/FastAPI)
1. `cd backend`
2. `python -m venv venv`
3. Activate virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `uvicorn app.main:app --reload`

### Frontend (React/Vite)
1. `cd frontend`
2. `npm install`
3. `npm run dev`

### Docker Compose
Run `docker compose up --build` from the root directory to spin up the frontend, backend, Redis, and Qdrant.
