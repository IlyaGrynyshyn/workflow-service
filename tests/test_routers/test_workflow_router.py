import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from database.models import Base, Workflow
from main import app
from routers.node import router
from schemas.workflow import WorkflowCreateSchema, WorkflowUpdateSchema
from services.workflow import WorkflowServices

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def workflow_services():
    return WorkflowServices()


def test_create_workflow(workflow_services, db_session):
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    create_url = app.url_path_for("create_workflow")
    response = client.post(create_url, json=workflow_data.dict())

    assert response.status_code == 201


def test_get_workflow(workflow_services, db_session):
    Base.metadata.create_all(bind=engine)

    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    created_workflow = workflow_services.create_workflow(workflow_data, db_session)

    get_url = app.url_path_for("get_workflow", workflow_id=created_workflow.id)
    response = client.get(get_url)

    assert response.status_code == 200
    assert response.json()["name"] == workflow_data.name
    Base.metadata.drop_all(bind=engine)


def test_update_workflow(workflow_services, db_session):
    Base.metadata.create_all(bind=engine)
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    create_url = app.url_path_for("create_workflow")
    create_response = client.post(create_url, json=workflow_data.dict())
    update_workflow = WorkflowUpdateSchema(name="New Workflow")

    get_url = app.url_path_for(
        "update_workflow", workflow_id=create_response.json()["id"]
    )
    response = client.put(get_url, json=update_workflow.dict())

    assert response.status_code == 200
    assert response.json()["name"] == update_workflow.name
    Base.metadata.drop_all(bind=engine)


def test_delete_workflow(workflow_services, db_session):
    Base.metadata.create_all(bind=engine)
    workflow_data = WorkflowCreateSchema(name="Test Workflow")
    created_workflow = workflow_services.create_workflow(workflow_data, db_session)

    get_url = app.url_path_for("delete_workflow", workflow_id=1)
    response = client.delete(get_url)

    assert response.status_code == 204
    Base.metadata.drop_all(bind=engine)
