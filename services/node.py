from fastapi import Depends, status, Response, HTTPException
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import (
    Node,
    ConditionNode,
    MessageNode,
    StartNode,
    EndNode,
    NodeType,
)
from schemas.node import (
    StartNodeSchema,
    EndNodeSchema,
    MessageNodeSchema,
    ConditionNodeSchema,
)
from services.utils import (
    get_object_by_id,
    save_object,
    delete_object,
)


class BaseNodeService:
    """
    Base class for node services.

    Attributes:
    - node_model: Model class representing the node.
    - node_schema: Schema class representing the node data structure.
    """

    def __init__(
        self,
        node_model: [StartNode | MessageNode | ConditionNode | EndNode],
        node_schema: [
            StartNodeSchema | EndNodeSchema | MessageNodeSchema | ConditionNodeSchema
        ],
    ):
        self.node_model = node_model
        self.node_schema = node_schema

    def create_node(
        self,
        node_data: [
            StartNodeSchema | EndNodeSchema | MessageNodeSchema | ConditionNodeSchema
        ],
        db: Session,
    ) -> Node | bool:
        if isinstance(node_data, (StartNodeSchema, EndNodeSchema)):
            existing_node = (
                db.query(self.node_model)
                .filter_by(workflow_id=node_data.workflow_id)
                .first()
            )
            if existing_node:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{self.node_model.__name__} already exists for this workflow",
                )
        node = self.node_model(**node_data.dict())
        return save_object(object=node, db_session=db)

    def get_node(self, node_id: int, db: Session): ...

    def update_node(
        self,
        node_id: int,
        node_data: [
            StartNodeSchema | EndNodeSchema | MessageNodeSchema | ConditionNodeSchema
        ],
        db: Session,
    ) -> Node:
        node = get_object_by_id(model=self.node_model, object_id=node_id, db_session=db)

        for attr, value in node_data.dict().items():
            setattr(node, attr, value)  # Update node properties

        return save_object(object=node, db_session=db)

    def delete_node(self, node_id: int, db: Session = Depends(get_db)):
        node = get_object_by_id(model=self.node_model, object_id=node_id, db_session=db)
        delete_object(object=node, db_session=db)
        return status.HTTP_204_NO_CONTENT


class NodeService:

    def __init__(self):
        # Create a factory for different types of nodes
        self.node_services = {
            NodeType.start: BaseNodeService(StartNode, StartNodeSchema),
            NodeType.message: BaseNodeService(MessageNode, MessageNodeSchema),
            NodeType.condition: BaseNodeService(ConditionNode, ConditionNodeSchema),
            NodeType.end: BaseNodeService(EndNode, EndNodeSchema),
        }

    def create_node(
        self,
        node_type: NodeType,
        node_data: [
            StartNodeSchema | EndNodeSchema | MessageNodeSchema | ConditionNodeSchema
        ],
        db: Session = Depends(get_db),
    ) -> Node:
        node_service = self.node_services.get(node_type)
        return node_service.create_node(node_data, db)

    def get_node(self, node_id: int, db: Session = Depends(get_db)) -> Node:
        node = get_object_by_id(model=Node, object_id=node_id, db_session=db)
        node_service = self.node_services.get(node.node_type)
        return node_service.node_schema.from_orm(node)

    def update_node(
        self,
        node_id: int,
        data: [
            StartNodeSchema | EndNodeSchema | MessageNodeSchema | ConditionNodeSchema
        ],
        db: Session = Depends(get_db),
    ) -> Node:
        node = get_object_by_id(model=Node, object_id=node_id, db_session=db)
        node_service = self.node_services.get(node.node_type)
        return node_service.update_node(node_id, data, db)

    def delete_node(self, node_id: int, db: Session = Depends(get_db)) -> Response:
        node = get_object_by_id(model=Node, object_id=node_id, db_session=db)
        node_service = self.node_services.get(node.node_type)
        return node_service.delete_node(node_id, db)
