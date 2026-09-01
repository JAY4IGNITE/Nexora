import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from app.core.config import settings
from app.ai.exceptions import AIConfigError, AIClientError
from app.ai.gemini_client import GeminiClient
from app.ai.agents.base import BaseAgent
from app.ai.agents.registry import AgentRegistry, register_agent
from app.ai.schemas.base import AIResponse

class MockPayload(BaseModel):
    message: str

class MockResponse(AIResponse[MockPayload]):
    pass

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-test")

def test_gemini_client_missing_key(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    with pytest.raises(AIConfigError):
        GeminiClient()

def test_gemini_client_initialization(mock_settings):
    client = GeminiClient()
    assert client.model_name == "gemini-test"

@pytest.mark.asyncio
@patch("app.ai.gemini_client.asyncio.to_thread")
async def test_gemini_client_success(mock_to_thread, mock_settings):
    mock_resp = MagicMock()
    mock_resp.text = '{"result": {"message": "hello"}, "reasoning_summary": "test", "confidence": 0.9, "evidence": [], "limitations": []}'
    mock_to_thread.return_value = mock_resp
    
    client = GeminiClient()
    result = await client.generate_structured("say hello", MockResponse)
    
    assert isinstance(result, MockResponse)
    assert result.result.message == "hello"
    assert result.confidence == 0.9

@pytest.mark.asyncio
@patch("app.ai.gemini_client.asyncio.to_thread")
async def test_gemini_client_api_error_exhausted(mock_to_thread, mock_settings):
    mock_to_thread.side_effect = Exception("Some weird error")
    
    client = GeminiClient()
    
    with pytest.raises(AIClientError) as exc_info:
        await client.generate_structured("say hello", MockResponse, max_retries=2, base_delay=0.01)
        
    assert "Unexpected error during generation" in str(exc_info.value)

@pytest.mark.asyncio
async def test_agent_registry():
    @register_agent
    class MockAgent(BaseAgent):
        @property
        def agent_name(self): return "MockAgent"
        @property
        def response_schema(self): return MockResponse
        
        async def validate_input(self, input_data): pass
        async def build_context(self, input_data): return "context"
        def build_prompt(self, input_data, context): return "prompt"
        
    agent = AgentRegistry.get_agent("MockAgent")
    assert agent.agent_name == "MockAgent"

@pytest.mark.asyncio
@patch("app.ai.gateway.AIGateway.request_structured_generation")
async def test_agent_run_lifecycle(mock_request):
    mock_request.return_value = MockResponse(
        result=MockPayload(message="lifecycle done"),
        reasoning_summary="test run",
        confidence=1.0,
        evidence=[],
        limitations=[]
    )
    
    agent = AgentRegistry.get_agent("MockAgent")
    result = await agent.run("input_test")
    
    assert result.result.message == "lifecycle done"
    assert result.confidence == 1.0

def test_ai_health_endpoint(mock_settings):
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/api/v1/ai/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
