import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from main import app
from schemas.node import (
    StartNodeSchema,
    EndNodeSchema,
    ConditionNodeSchema,
    MessageNodeSchema,
    NodeStatus,
)
from services.node import NodeService
from services.workflow import WorkflowService

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


class BaseTestConfig:
    @pytest.fixture(scope="function")
    def db_session(self):
        session = SessionLocal()
        yield session
        session.close()

    @pytest.fixture
    def workflow_services(self):
        return WorkflowService()

    @pytest.fixture
    def node_services(self):
        return NodeService()


class TestCreateNodeRouter(BaseTestConfig):
    def test_create_start_node(self):
        node_data = StartNodeSchema(workflow_id=123, next_node_id=1)
        create_url = app.url_path_for("create_start_node")
        response1 = client.post(create_url, json=node_data.dict())

        assert response1.status_code == 201

        response2 = client.post(create_url, json=node_data.dict())
        assert response2.status_code == 400
        assert response2.json() == {
            "detail": "StartNode already exists for this workflow"
        }

    def test_create_message_node(self):
        node_data = MessageNodeSchema(
            workflow_id=123, message="Message", status=NodeStatus.open, next_node_id=2
        )
        create_url = app.url_path_for("create_message_node")
        response = client.post(create_url, json=node_data.dict())

        assert response.status_code == 201
        assert response.json()["message"] == node_data.message
        assert response.json()["status"] == node_data.status
        assert response.json()["workflow_id"] == node_data.workflow_id

    def test_create_condition_node(self):
        node_data = ConditionNodeSchema(
            workflow_id=123, condition="Condition", yes_node_id=2, no_node_id=3
        )
        create_url = app.url_path_for("create_condition_node")
        response = client.post(create_url, json=node_data.dict())

        assert response.status_code == 201
        assert response.json()["workflow_id"] == node_data.workflow_id
        assert response.json()["condition"] == node_data.condition
        assert response.json()["yes_node_id"] == node_data.yes_node_id
        assert response.json()["no_node_id"] == node_data.no_node_id

    def test_create_end_node(self):
        node_data = EndNodeSchema(workflow_id=123)
        create_url = app.url_path_for("create_end_node")
        response = client.post(create_url, json=node_data.dict())
        assert response.status_code == 201
        assert response.json()["workflow_id"] == node_data.workflow_id


class TestGetNodeRouter(BaseTestConfig):
    def test_get_node(self, node_services, db_session):
        node_data = StartNodeSchema(workflow_id=123, next_node_id=2)
        create_url = app.url_path_for("create_start_node")
        client.post(create_url, json=node_data.dict())

        get_url = app.url_path_for("get_node", node_id=1)
        response_get = client.get(get_url)
        assert response_get.status_code == 200
        assert response_get.json()["workflow_id"] == node_data.workflow_id


class TestUpdateNodeRouter(BaseTestConfig):
    def test_update_start_node(self, node_services, db_session):
        node_data = StartNodeSchema(workflow_id=123, next_node_id=2)
        create_url = app.url_path_for("create_start_node")
        client.post(create_url, json=node_data.dict())

        new_node_data = StartNodeSchema(workflow_id=123, next_node_id=100)
        update_url = app.url_path_for("update_start_node", node_id=1)
        response = client.put(update_url, json=new_node_data.dict())

        assert response.status_code == 200
        assert response.json()["workflow_id"] == node_data.workflow_id
        assert response.json()["next_node_id"] == new_node_data.next_node_id

    def test_update_message_node(self, node_services, db_session):
        node_data = MessageNodeSchema(
            workflow_id=123, message="Message", status=NodeStatus.open, next_node_id=2
        )
        create_url = app.url_path_for("create_start_node")
        client.post(create_url, json=node_data.dict())

        new_node_data = MessageNodeSchema(
            workflow_id=123,
            message="New Message",
            status=NodeStatus.sent,
            next_node_id=2,
        )
        update_url = app.url_path_for("update_message_node", node_id=1)
        response = client.put(update_url, json=new_node_data.dict())

        assert response.status_code == 200
        assert response.json()["workflow_id"] == node_data.workflow_id
        assert response.json()["message"] == new_node_data.message
        assert response.json()["status"] == new_node_data.status
        assert response.json()["next_node_id"] == new_node_data.next_node_id

    def test_update_condition_node(self, node_services, db_session):
        node_data = ConditionNodeSchema(
            workflow_id=123, condition="Condition", yes_node_id=2, no_node_id=3
        )
        create_url = app.url_path_for("create_condition_node")
        client.post(create_url, json=node_data.dict())

        new_node_data = ConditionNodeSchema(
            workflow_id=123,
            condition="New Condition",
            yes_node_id=22,
            no_node_id=11,
        )
        update_url = app.url_path_for("update_condition_node", node_id=1)
        response = client.put(update_url, json=new_node_data.dict())
        assert response.status_code == 200

        assert response.json()["workflow_id"] == node_data.workflow_id
        assert response.json()["condition"] == new_node_data.condition
        assert response.json()["yes_node_id"] == new_node_data.yes_node_id
        assert response.json()["no_node_id"] == new_node_data.no_node_id

    def test_update_end_node(self):
        node_data = EndNodeSchema(workflow_id=123)
        create_url = app.url_path_for("create_condition_node")
        client.post(create_url, json=node_data.dict())

        new_node_data = EndNodeSchema(workflow_id=111)
        update_url = app.url_path_for("update_end_node", node_id=1)
        response = client.put(update_url, json=new_node_data.dict())
        assert response.status_code == 200
        assert response.json()["workflow_id"] == new_node_data.workflow_id


class TestDeleteNode(BaseTestConfig):
    def test_delete_node(self):
        node_data = EndNodeSchema(workflow_id=123)
        create_url = app.url_path_for("create_condition_node")
        client.post(create_url, json=node_data.dict())

        delete_url = app.url_path_for("delete_node", node_id=1)
        response = client.delete(delete_url)
        assert response.status_code == 204
