import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import Base
from schemas.workflow import WorkflowCreateSchema, WorkflowUpdateSchema
from services.workflow import WorkflowService

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def workflow_services():
    return WorkflowService()


def test_create_workflow(workflow_services, db_session):
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    workflow = workflow_services.create_workflow(workflow_data, db_session)
    assert workflow.name == "Test Workflow"
    assert workflow.id is not None


def test_get_workflow(workflow_services, db_session):
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    workflow = workflow_services.create_workflow(workflow_data, db_session)

    fetched_workflow = workflow_services.get_workflow(workflow.id, db_session)

    assert fetched_workflow.id == workflow.id
    assert fetched_workflow is not None


def test_update_workflow(workflow_services, db_session):
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    workflow = workflow_services.create_workflow(workflow_data, db_session)
    update_data = WorkflowUpdateSchema(name="Updated Workflow")
    updated_workflow = workflow_services.update_workflow(
        workflow.id, update_data, db_session
    )
    assert updated_workflow is not None
    assert updated_workflow.name == "Updated Workflow"


def test_delete_workflow(workflow_services, db_session):
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    workflow = workflow_services.create_workflow(workflow_data, db_session)
    result = workflow_services.delete_workflow(workflow.id, db_session)
    assert result is True
