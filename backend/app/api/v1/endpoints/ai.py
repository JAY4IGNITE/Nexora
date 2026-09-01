from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.api.deps import get_current_user
from app.ai.gateway import ai_gateway
from app.ai.schemas.base import AIResponse

router = APIRouter()

class TestPromptRequest(BaseModel):
    prompt: str

class TestResult(BaseModel):
    message: str

class TestResponse(AIResponse[TestResult]):
    pass

@router.get("/health")
def ai_health():
    """Returns 200 OK if the AI configuration exists."""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI Foundation is not configured.")
    return {"status": "ok", "model": settings.GEMINI_MODEL}

@router.post("/test", response_model=TestResponse)
async def ai_test(
    request: TestPromptRequest,
    current_user: dict = Depends(get_current_user)
):
    """Protected endpoint for testing the AI Foundation."""
    # For testing purposes only. In production, this might be restricted further.
    try:
        response = await ai_gateway.request_structured_generation(
            agent_name="TestAgent",
            prompt=request.prompt,
            response_schema=TestResponse,
            system_instruction="You are a test agent responding cleanly."
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
