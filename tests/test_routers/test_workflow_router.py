import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.testclient import TestClient


from database.config import Base
from main import app
from schemas.workflow import WorkflowCreateSchema, WorkflowUpdateSchema
from services.workflow import WorkflowService

client = TestClient(app)

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def workflow_services():
    return WorkflowService()


class TestWorkflowRouter:
    def test_create_workflow(self,workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        create_url = app.url_path_for("create_workflow")
        response = client.post(create_url, json=workflow_data.dict())

        assert response.status_code == 201


    def test_get_workflow(self, workflow_services, db_session):
        Base.metadata.create_all(bind=engine)
        # workflow_data = WorkflowCreateSchema(name="Test Workflow")
        # created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        create_url = app.url_path_for("create_workflow")
        response = client.post(create_url, json=workflow_data.dict())


        get_url = app.url_path_for("get_workflow", workflow_id=response.json()["id"])
        response = client.get(get_url)

        assert response.status_code == 200
        assert response.json()["name"] == workflow_data.name

        Base.metadata.drop_all(bind=engine)


    def test_update_workflow(self, workflow_services, db_session):
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


    def test_delete_workflow(self, workflow_services, db_session):
        Base.metadata.create_all(bind=engine)
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        create_url = app.url_path_for("create_workflow")
        created_workflow = client.post(create_url, json=workflow_data.dict())

        get_url = app.url_path_for("delete_workflow", workflow_id=created_workflow.json()["id"])
        response = client.delete(get_url)

        assert response.status_code == 204
        Base.metadata.drop_all(bind=engine)

