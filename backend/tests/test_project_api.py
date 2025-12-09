import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base, get_db
from app.models.project import Project, Requirement
from main import app
import tempfile
import os
import json

@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    # Create test engine and session
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Cleanup
    app.dependency_overrides.clear()
    engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

def test_create_project_success(client, test_db):
    """Test successful project creation"""
    project_data = {
        "name": "Test Project",
        "requirements": ["chair", "table", "lamp"]
    }
    
    response = client.post("/api/projects/", json=project_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert len(data["requirements"]) == 3
    assert "chair" in data["requirements"]
    assert "id" in data
    assert "created_at" in data

def test_create_project_invalid_empty_name(client, test_db):
    """Test project creation with empty name"""
    project_data = {
        "name": "",
        "requirements": ["chair"]
    }
    
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 422  # Validation error

def test_create_project_invalid_empty_requirements(client, test_db):
    """Test project creation with empty requirements"""
    project_data = {
        "name": "Test Project",
        "requirements": []
    }
    
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 422  # Validation error

def test_create_project_invalid_long_name(client, test_db):
    """Test project creation with name too long"""
    project_data = {
        "name": "x" * 256,  # Too long
        "requirements": ["chair"]
    }
    
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 422  # Validation error

def test_get_project_success(client, test_db):
    """Test successful project retrieval"""
    # First create a project
    project_data = {
        "name": "Test Project",
        "requirements": ["chair", "table"]
    }
    
    create_response = client.post("/api/projects/", json=project_data)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/api/projects/{project_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Project"
    assert len(data["requirements"]) == 2
    assert "chair" in data["requirements"]
    assert "table" in data["requirements"]

def test_get_project_not_found(client, test_db):
    """Test retrieving non-existent project"""
    response = client.get("/api/projects/non-existent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_get_all_projects_empty(client, test_db):
    """Test retrieving all projects when none exist"""
    response = client.get("/api/projects/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_projects_with_data(client, test_db):
    """Test retrieving all projects with existing data"""
    # Create multiple projects
    projects_data = [
        {"name": "Project 1", "requirements": ["chair", "table"]},
        {"name": "Project 2", "requirements": ["lamp", "sofa"]},
        {"name": "Project 3", "requirements": ["window", "door"]}
    ]
    
    created_ids = []
    for project_data in projects_data:
        response = client.post("/api/projects/", json=project_data)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])
    
    # Retrieve all projects
    response = client.get("/api/projects/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Check that all created projects are returned
    returned_ids = [project["id"] for project in data]
    for created_id in created_ids:
        assert created_id in returned_ids
    
    # Check project names
    returned_names = [project["name"] for project in data]
    assert "Project 1" in returned_names
    assert "Project 2" in returned_names
    assert "Project 3" in returned_names

def test_project_requirements_normalization(client, test_db):
    """Test that requirements are normalized (lowercase, trimmed)"""
    project_data = {
        "name": "Test Project",
        "requirements": ["  CHAIR  ", "Table", "  lamp"]
    }
    
    response = client.post("/api/projects/", json=project_data)
    
    assert response.status_code == 201
    data = response.json()
    requirements = data["requirements"]
    
    # Requirements should be normalized to lowercase and trimmed
    assert "chair" in requirements
    assert "table" in requirements
    assert "lamp" in requirements
    
    # Original formats should not be present
    assert "  CHAIR  " not in requirements
    assert "Table" not in requirements

def test_api_content_type_validation(client, test_db):
    """Test API validates content type"""
    # Send invalid content type
    response = client.post(
        "/api/projects/",
        data="invalid data",
        headers={"Content-Type": "text/plain"}
    )
    
    assert response.status_code == 422

def test_api_missing_fields(client, test_db):
    """Test API validates required fields"""
    # Missing name
    response = client.post("/api/projects/", json={"requirements": ["chair"]})
    assert response.status_code == 422
    
    # Missing requirements
    response = client.post("/api/projects/", json={"name": "Test"})
    assert response.status_code == 422