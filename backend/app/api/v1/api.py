from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Future modules placeholders:
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
# ...
