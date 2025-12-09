import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreateRequest
from app.models.project import Project, Requirement
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
    engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass

@pytest.mark.asyncio
async def test_create_project_success(test_db):
    """Test successful project creation"""
    service = ProjectService(test_db)
    
    project_data = ProjectCreateRequest(
        name="Test Project",
        requirements=["chair", "table", "lamp"]
    )
    
    result = await service.create_project(project_data)
    
    assert result.name == "Test Project"
    assert len(result.requirements) == 3
    assert "chair" in result.requirements
    assert "table" in result.requirements
    assert "lamp" in result.requirements
    assert result.id is not None
    assert result.created_at is not None

@pytest.mark.asyncio
async def test_create_project_requirements_normalized(test_db):
    """Test that requirements are normalized during creation"""
    service = ProjectService(test_db)
    
    project_data = ProjectCreateRequest(
        name="Test Project",
        requirements=["  CHAIR  ", "Table", "  lamp"]
    )
    
    result = await service.create_project(project_data)
    
    # Requirements should be normalized to lowercase and trimmed
    assert "chair" in result.requirements
    assert "table" in result.requirements
    assert "lamp" in result.requirements

@pytest.mark.asyncio
async def test_get_project_success(test_db):
    """Test successful project retrieval"""
    service = ProjectService(test_db)
    
    # Create project first
    project_data = ProjectCreateRequest(
        name="Test Project",
        requirements=["chair", "table"]
    )
    created_project = await service.create_project(project_data)
    
    # Retrieve project
    result = await service.get_project(created_project.id)
    
    assert result is not None
    assert result.id == created_project.id
    assert result.name == "Test Project"
    assert len(result.requirements) == 2
    assert "chair" in result.requirements
    assert "table" in result.requirements

@pytest.mark.asyncio
async def test_get_project_not_found(test_db):
    """Test retrieving non-existent project"""
    service = ProjectService(test_db)
    
    result = await service.get_project("non-existent-id")
    
    assert result is None

@pytest.mark.asyncio
async def test_get_all_projects_empty(test_db):
    """Test retrieving all projects when none exist"""
    service = ProjectService(test_db)
    
    result = await service.get_all_projects()
    
    assert isinstance(result, list)
    assert len(result) == 0

@pytest.mark.asyncio
async def test_get_all_projects_with_data(test_db):
    """Test retrieving all projects with existing data"""
    service = ProjectService(test_db)
    
    # Create multiple projects
    projects_data = [
        ProjectCreateRequest(name="Project 1", requirements=["chair", "table"]),
        ProjectCreateRequest(name="Project 2", requirements=["lamp", "sofa"]),
        ProjectCreateRequest(name="Project 3", requirements=["window", "door"])
    ]
    
    created_projects = []
    for project_data in projects_data:
        created_project = await service.create_project(project_data)
        created_projects.append(created_project)
    
    # Retrieve all projects
    result = await service.get_all_projects()
    
    assert isinstance(result, list)
    assert len(result) == 3
    
    # Check that all created projects are returned
    returned_ids = [project.id for project in result]
    for created_project in created_projects:
        assert created_project.id in returned_ids
    
    # Check project names
    returned_names = [project.name for project in result]
    assert "Project 1" in returned_names
    assert "Project 2" in returned_names
    assert "Project 3" in returned_names

@pytest.mark.asyncio
async def test_create_project_database_rollback_on_error(test_db):
    """Test that database operations are rolled back on error"""
    service = ProjectService(test_db)
    
    # Create a project with valid data first
    project_data = ProjectCreateRequest(
        name="Test Project",
        requirements=["chair"]
    )
    
    # Mock a database error by closing the session
    original_commit = test_db.commit
    test_db.commit = lambda: (_ for _ in ()).throw(Exception("Database error"))
    
    # Attempt to create project - should fail and rollback
    with pytest.raises(Exception):
        await service.create_project(project_data)
    
    # Restore original commit method
    test_db.commit = original_commit
    
    # Verify no project was created
    projects = test_db.query(Project).all()
    assert len(projects) == 0
    
    # Verify no requirements were created
    requirements = test_db.query(Requirement).all()
    assert len(requirements) == 0

@pytest.mark.asyncio
async def test_project_with_duplicate_requirements(test_db):
    """Test creating project with duplicate requirements"""
    service = ProjectService(test_db)
    
    project_data = ProjectCreateRequest(
        name="Test Project",
        requirements=["chair", "chair", "table", "chair"]
    )
    
    result = await service.create_project(project_data)
    
    # All requirements should be stored, even duplicates
    # (Business logic for deduplication can be added later if needed)
    assert len(result.requirements) == 4
    assert result.requirements.count("chair") == 3
    assert result.requirements.count("table") == 1