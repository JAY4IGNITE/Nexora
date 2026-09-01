import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

# We need to mock the get_current_user dependency to bypass Firebase auth
from app.api.deps import get_current_user
from app.ai.schemas.skill import SkillExtractionResponse, StudentSkillExtraction, ExtractedSkill

def mock_get_current_user():
    return {"id": "11111111-1111-1111-1111-111111111111", "email": "test@student.com", "role": "STUDENT"}

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

@pytest.fixture
def mock_supabase():
    with patch("app.api.v1.endpoints.student.get_supabase_client") as mock:
        yield mock

@pytest.fixture
def mock_r2():
    with patch("app.api.v1.endpoints.student.r2_storage.upload_resume") as mock:
        yield mock

@pytest.fixture
def mock_agent_run():
    with patch("app.ai.agents.base.BaseAgent.run") as mock:
        yield mock

def test_resume_analyze_invalid_type():
    response = client.post(
        "/api/v1/student/resume/analyze",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF resumes" in response.json()["detail"]

def test_resume_analyze_success(mock_supabase, mock_r2, mock_agent_run):
    # We must patch asyncio.to_thread if we mock anything async, but the endpoint is async
    # TestClient in fastAPI handles async automatically, but our mock_r2 and mock_agent_run are async.
    mock_r2.return_value = "resumes/123/test.pdf"
    
    mock_agent_run.return_value = SkillExtractionResponse(
        result=StudentSkillExtraction(
            skills=[
                ExtractedSkill(
                    name="Python",
                    proficiency="INTERMEDIATE",
                    confidence=0.9,
                    evidence_quote="Built a Django backend"
                )
            ]
        ),
        reasoning_summary="Found Python",
        confidence=0.9,
        evidence=[],
        limitations=[]
    )
    
    mock_db = MagicMock()
    mock_supabase.return_value = mock_db
    mock_db.table().select().in_().execute.return_value = MagicMock(data=[{"id": "uuid-1", "name": "Python"}])
    mock_db.table().upsert().execute.return_value = MagicMock(data=[{"id": "ss-uuid-1"}])
    
    with patch("app.api.v1.endpoints.student.PyPDF2.PdfReader") as mock_pdf:
        mock_pdf_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Resume text Python Django"
        mock_pdf_instance.pages = [mock_page]
        mock_pdf.return_value = mock_pdf_instance
        
        response = client.post(
            "/api/v1/student/resume/analyze",
            files={"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
        )
        
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["skills_added"] == 1
    
def test_get_student_skills(mock_supabase):
    mock_db = MagicMock()
    mock_supabase.return_value = mock_db
    mock_db.table().select().eq().execute.return_value = MagicMock(data=[{"skill_name": "Python", "proficiency": 3}])
    
    response = client.get("/api/v1/student/skills")
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 1

def test_set_target_role(mock_supabase):
    mock_db = MagicMock()
    mock_supabase.return_value = mock_db
    mock_db.table().upsert().execute.return_value = MagicMock(data=[{"id": "tr-1"}])
    
    response = client.post("/api/v1/student/target-role", json={"job_role_id": "role-uuid-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_skill_gaps(mock_supabase):
    mock_db = MagicMock()
    mock_supabase.return_value = mock_db
    mock_db.table().select().eq().execute.return_value = MagicMock(data=[{"skill_name": "ML", "gap_status": "GAP"}])
    
    response = client.get("/api/v1/student/skill-gaps")
    assert response.status_code == 200
    assert response.json()["gaps"][0]["gap_status"] == "GAP"
