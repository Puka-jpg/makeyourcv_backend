from fastapi.testclient import TestClient

from main import app


from dependencies.auth_dependencies.auth import get_current_user
from models import User

def test_adk_chat_endpoint():
    # Mock user for authentication dependency
    mock_user = User(
        id="test_user_id",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="hashed_password"
    )

    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # TestClient handles the async app synchronously for testing
    with TestClient(app) as client:
        # Note: endpoint expects Form data (multipart/form-data), not JSON
        payload = {
            "message": "Hello Agent",
        }
        # Use data=payload for Form data
        response = client.post("/api/v1/adk/chat", data=payload)

        # Clean up override
        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"]
