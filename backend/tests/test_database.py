import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base, get_db
from app.models.project import Project, Requirement, Detection
import tempfile
import os

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
    
    # Create session
    db = TestingSessionLocal()
    
    yield db
    
    # Cleanup
    db.close()
    engine.dispose()  # Close all connections
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        # On Windows, sometimes the file is still locked
        pass

def test_create_project(test_db):
    """Test creating a project"""
    project = Project(name="Test Project")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.created_at is not None

def test_create_requirement(test_db):
    """Test creating a requirement"""
    # Create project first
    project = Project(name="Test Project")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    
    # Create requirement
    requirement = Requirement(project_id=project.id, object_name="chair")
    test_db.add(requirement)
    test_db.commit()
    test_db.refresh(requirement)
    
    assert requirement.id is not None
    assert requirement.project_id == project.id
    assert requirement.object_name == "chair"

def test_create_detection(test_db):
    """Test creating a detection"""
    # Create project first
    project = Project(name="Test Project")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    
    # Create detection
    detection = Detection(
        project_id=project.id,
        image_path="/test/path.jpg",
        object_name="chair",
        confidence=0.85,
        bbox_x=100.0,
        bbox_y=200.0,
        bbox_width=50.0,
        bbox_height=75.0
    )
    test_db.add(detection)
    test_db.commit()
    test_db.refresh(detection)
    
    assert detection.id is not None
    assert detection.project_id == project.id
    assert detection.confidence == 0.85

def test_project_relationships(test_db):
    """Test project relationships with requirements and detections"""
    # Create project
    project = Project(name="Test Project")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    
    # Create requirements
    req1 = Requirement(project_id=project.id, object_name="chair")
    req2 = Requirement(project_id=project.id, object_name="table")
    test_db.add_all([req1, req2])
    test_db.commit()
    
    # Create detection
    detection = Detection(
        project_id=project.id,
        image_path="/test/path.jpg",
        object_name="chair",
        confidence=0.85
    )
    test_db.add(detection)
    test_db.commit()
    
    # Test relationships
    project = test_db.query(Project).filter(Project.id == project.id).first()
    assert len(project.requirements) == 2
    assert len(project.detections) == 1
    assert project.requirements[0].object_name in ["chair", "table"]
    assert project.detections[0].object_name == "chair"