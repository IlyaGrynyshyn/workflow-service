import pytest
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from database.models import Base
from main import app
from schemas.node import (
    StartNodeSchema,
    MessageNodeSchema,
    ConditionNodeSchema,
    EndNodeSchema,
    NodeType,
    NodeStatus,
)
from schemas.workflow import WorkflowCreateSchema
from services.node import NodeService
from services.workflow import WorkflowServices

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
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
        return WorkflowServices()

    @pytest.fixture
    def node_services(self):
        return NodeService()


class TestCreateNodeService(BaseTestConfig):

    def test_create_start_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        node_data = StartNodeSchema(workflow_id=created_workflow.id, next_node_id=2)
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.start, db=db_session
        )
        assert created_node.workflow_id == created_workflow.id
        assert created_node.next_node_id == 2

    def test_create_message_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        node_data = MessageNodeSchema(
            workflow_id=created_workflow.id,
            message="Test Message",
            status=NodeStatus.open,
            next_node_id=3,
        )
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.message, db=db_session
        )
        assert created_node.workflow_id == created_workflow.id
        assert created_node.status == NodeStatus.open
        assert created_node.next_node_id == 3

    def test_create_condition_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        node_data = ConditionNodeSchema(
            workflow_id=created_workflow.id,
            condition="Test Condition",
            yes_node_id=5,
            no_node_id=2,
        )
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.condition, db=db_session
        )

        assert created_node.workflow_id == created_workflow.id
        assert created_node.condition == node_data.condition
        assert created_node.yes_node_id == 5
        assert created_node.no_node_id == 2

    def test_create_end_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        node_data = EndNodeSchema(workflow_id=created_workflow.id)
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.end, db=db_session
        )

        assert created_node.workflow_id == created_workflow.id


class TestUpdateNodeService(BaseTestConfig):

    def test_update_start_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)

        node_data = StartNodeSchema(workflow_id=created_workflow.id, next_node_id=2)
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.start, db=db_session
        )

        new_data = StartNodeSchema(workflow_id=created_workflow.id, next_node_id=5)
        updated_node = node_services.update_node(
            node_id=created_node.id, data=new_data, db=db_session
        )
        assert updated_node.next_node_id == new_data.next_node_id

    def test_update_message_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)

        node_data = MessageNodeSchema(
            workflow_id=created_workflow.id,
            message="Test Message",
            status=NodeStatus.open,
            next_node_id=3,
        )
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.message, db=db_session
        )

        new_data = MessageNodeSchema(
            workflow_id=created_workflow.id,
            message="Updated Message",
            status=NodeStatus.sent,
            next_node_id=3,
        )

        updated_node = node_services.update_node(
            node_id=created_node.id, data=new_data, db=db_session
        )

        assert updated_node.message == "Updated Message"
        assert updated_node.status == NodeStatus.sent

        assert updated_node.message != "Test Message"
        assert updated_node.status != NodeStatus.open

    def test_update_condition_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        node_data = ConditionNodeSchema(
            workflow_id=created_workflow.id,
            condition="Test Condition",
            yes_node_id=5,
            no_node_id=2,
        )
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.condition, db=db_session
        )
        new_data = ConditionNodeSchema(
            workflow_id=created_workflow.id,
            condition="New Condition",
            yes_node_id=5,
            no_node_id=2,
        )
        updated_node = node_services.update_node(
            node_id=created_node.id, data=new_data, db=db_session
        )
        assert updated_node.condition == "New Condition"
        assert updated_node.condition != "Test Condition"
        assert updated_node.workflow_id == created_workflow.id


class TestDeleteNodeService(BaseTestConfig):
    def test_delete_node(self, node_services, workflow_services, db_session):
        workflow_data = WorkflowCreateSchema(name="Test Workflow")
        created_workflow = workflow_services.create_workflow(workflow_data, db_session)
        node_data = ConditionNodeSchema(
            workflow_id=created_workflow.id,
            condition="Test Condition",
            yes_node_id=5,
            no_node_id=2,
        )
        created_node = node_services.create_node(
            node_data=node_data, node_type=NodeType.condition, db=db_session
        )
        delete_node = node_services.delete_node(node_id=created_node.id, db=db_session)

        assert delete_node == status.HTTP_204_NO_CONTENT
