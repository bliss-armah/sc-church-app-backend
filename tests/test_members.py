"""
Example test file for member endpoints.
Run with: pytest
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_member():
    """Test creating a new member"""
    member_data = {
        "first_name": "Test",
        "last_name": "User",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "date_joined": "2024-01-15",
        "email": "test@example.com"
    }
    
    response = client.post("/api/v1/members/", json=member_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert "id" in data


def test_list_members():
    """Test listing members with pagination"""
    response = client.get("/api/v1/members/?page=1&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_create_member_validation_error():
    """Test validation error when required fields are missing"""
    member_data = {
        "first_name": "Test"
        # Missing required fields
    }
    
    response = client.post("/api/v1/members/", json=member_data)
    assert response.status_code == 422  # Validation error
