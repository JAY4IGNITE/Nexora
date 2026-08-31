from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def check_health():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "NEXORA API is running"}
