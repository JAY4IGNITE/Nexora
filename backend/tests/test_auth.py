import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from app.models.user import UserRole

client = TestClient(app)

@pytest.fixture
def mock_verify_token():
    with patch("app.api.deps.auth.verify_id_token") as mock:
        yield mock

@pytest.fixture
def mock_get_user():
    with patch("app.api.deps.get_user_by_firebase_uid") as mock:
        yield mock

@pytest.fixture
def mock_create_user():
    with patch("app.api.deps.create_user") as mock:
        yield mock

def test_read_users_me_missing_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403 # HTTPBearer missing token returns 403

def test_read_users_me_invalid_token(mock_verify_token):
    from firebase_admin import auth
    mock_verify_token.side_effect = auth.InvalidIdTokenError("Invalid token")
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Firebase ID token"}

def test_read_users_me_success_provisioning(mock_verify_token, mock_get_user, mock_create_user):
    # Mock firebase token verification
    mock_verify_token.return_value = {"uid": "new_uid", "email": "test@example.com"}
    
    # Mock user not found in DB
    mock_get_user.return_value = None
    
    # Mock user creation
    from app.models.user import User
    mock_create_user.return_value = User(
        id="00000000-0000-0000-0000-000000000000",
        firebase_uid="new_uid",
        email="test@example.com",
        role=UserRole.STUDENT,
        is_active=True,
        created_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z"
    )
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "STUDENT"
