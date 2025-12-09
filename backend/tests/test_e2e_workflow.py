import pytest
import asyncio
import os
import tempfile
from httpx import AsyncClient
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from app.database.connection import get_db, create_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_e2e.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_test_db():
    """Setup test database"""
    # Create tables with the test engine
    from app.models.project import Base
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup
    try:
        if os.path.exists("test_e2e.db"):
            os.remove("test_e2e.db")
    except PermissionError:
        pass  # File might be locked on Windows

@pytest.fixture
def test_image():
    """Create a test image file"""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

class TestEndToEndWorkflow:
    """End-to-end integration tests for complete user workflow"""
    
    def test_complete_user_workflow(self, client, setup_test_db, test_image):
        """Test the complete user workflow from project creation to dashboard"""
        
        # Step 1: Create a new project
        project_data = {
            "name": "Test Construction Project",
            "requirements": ["chair", "table", "window", "door"]
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        
        project = response.json()
        project_id = project["id"]
        assert project["name"] == project_data["name"]
        assert len(project["requirements"]) == 4
        
        # Step 2: Upload images for object detection
        with open(test_image, "rb") as f:
            files = {"files": ("test_image.jpg", f, "image/jpeg")}
            response = client.post(f"/api/projects/{project_id}/upload", files=files)
        
        assert response.status_code == 200
        upload_result = response.json()
        assert "uploaded_files" in upload_result
        assert "detection_results" in upload_result
        assert len(upload_result["uploaded_files"]) == 1
        
        # Step 3: Get project progress
        response = client.get(f"/api/projects/{project_id}/progress")
        assert response.status_code == 200
        
        progress = response.json()
        assert "completion_percentage" in progress
        assert "requirement_matches" in progress
        assert "detection_summary" in progress
        assert progress["project_id"] == project_id
        
        # Step 4: Retrieve project details
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        
        retrieved_project = response.json()
        assert retrieved_project["id"] == project_id
        assert retrieved_project["name"] == project_data["name"]
        
        # Step 5: List all projects
        response = client.get("/api/projects")
        assert response.status_code == 200
        
        projects = response.json()
        assert len(projects) >= 1
        assert any(p["id"] == project_id for p in projects)
    
    def test_health_check_endpoints(self, client, setup_test_db):
        """Test health check and monitoring endpoints"""
        
        # Basic health check
        response = client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        
        # Detailed health check
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        detailed_health = response.json()
        assert "status" in detailed_health
        assert "timestamp" in detailed_health
        assert "system" in detailed_health
        assert "application" in detailed_health
        
        # Metrics endpoint
        response = client.get("/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        assert "system" in metrics
        assert "application" in metrics
    
    def test_error_handling_workflow(self, client, setup_test_db):
        """Test error handling in the workflow"""
        
        # Test invalid project creation
        invalid_project = {"name": "", "requirements": []}
        response = client.post("/api/projects", json=invalid_project)
        assert response.status_code == 422  # Validation error
        
        # Test accessing non-existent project
        response = client.get("/api/projects/non-existent-id")
        assert response.status_code == 404
        
        # Test uploading to non-existent project
        with open(test_image, "rb") as f:
            files = {"files": ("test.jpg", f, "image/jpeg")}
            response = client.post("/api/projects/non-existent-id/upload", files=files)
        assert response.status_code == 404
        
        # Test progress for non-existent project
        response = client.get("/api/projects/non-existent-id/progress")
        assert response.status_code == 404
    
    def test_multiple_image_upload_workflow(self, client, setup_test_db, test_image):
        """Test workflow with multiple image uploads"""
        
        # Create project
        project_data = {
            "name": "Multi-Image Test Project",
            "requirements": ["chair", "table", "sofa"]
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Create multiple test images
        test_images = []
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=['red', 'green', 'blue'][i])
            temp_file = tempfile.NamedTemporaryFile(suffix=f'_test_{i}.jpg', delete=False)
            img.save(temp_file.name, 'JPEG')
            temp_file.close()
            test_images.append(temp_file.name)
        
        try:
            # Upload multiple images
            files = []
            for i, img_path in enumerate(test_images):
                with open(img_path, "rb") as f:
                    files.append(("files", (f"test_image_{i}.jpg", f.read(), "image/jpeg")))
            
            response = client.post(f"/api/projects/{project_id}/upload", files=files)
            assert response.status_code == 200
            
            upload_result = response.json()
            assert len(upload_result["uploaded_files"]) == 3
            assert len(upload_result["detection_results"]) == 3
            
            # Check progress after multiple uploads
            response = client.get(f"/api/projects/{project_id}/progress")
            assert response.status_code == 200
            
            progress = response.json()
            assert "completion_percentage" in progress
            assert "detection_summary" in progress
            
        finally:
            # Cleanup test images
            for img_path in test_images:
                if os.path.exists(img_path):
                    os.remove(img_path)
    
    def test_concurrent_requests(self, client, setup_test_db):
        """Test handling of concurrent requests"""
        
        # Create multiple projects concurrently
        project_data_list = [
            {"name": f"Concurrent Project {i}", "requirements": ["chair", "table"]}
            for i in range(5)
        ]
        
        responses = []
        for project_data in project_data_list:
            response = client.post("/api/projects", json=project_data)
            responses.append(response)
        
        # Verify all projects were created successfully
        project_ids = []
        for i, response in enumerate(responses):
            assert response.status_code == 201
            project = response.json()
            assert project["name"] == f"Concurrent Project {i}"
            project_ids.append(project["id"])
        
        # Verify all projects can be retrieved
        for project_id in project_ids:
            response = client.get(f"/api/projects/{project_id}")
            assert response.status_code == 200
        
        # List all projects and verify count
        response = client.get("/api/projects")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) >= 5

@pytest.mark.asyncio
async def test_async_workflow():
    """Test async workflow using AsyncClient"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test basic endpoints
        response = await ac.get("/")
        assert response.status_code == 200
        
        response = await ac.get("/health")
        assert response.status_code == 200
        
        # Test project creation
        project_data = {
            "name": "Async Test Project",
            "requirements": ["chair", "table"]
        }
        
        response = await ac.post("/api/projects", json=project_data)
        assert response.status_code == 201