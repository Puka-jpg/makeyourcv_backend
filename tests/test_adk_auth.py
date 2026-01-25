
from uuid import uuid4

from fastapi.testclient import TestClient

from dependencies.auth_dependencies.auth import get_current_user
from main import app
from models import User

# Mock user
mock_user = User(id=uuid4(), email="test@example.com", first_name="Test", last_name="User")

def mock_get_current_user():
    return mock_user

def test_adk_chat_endpoint_authenticated():
    # Override the dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    with TestClient(app) as client:
        payload = {
            "message": "Hello Agent with Auth"
        }
        # session_id is optional now
        response = client.post("/api/v1/adk/chat", json=payload)
    
        print(f"Response Status: {response.status_code}")
        if response.status_code != 200:
             print(f"Error Response: {response.json()}")
             
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"]
        
    # Clean up
    app.dependency_overrides = {}
