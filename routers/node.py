from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.config import get_db
from schemas.node import (
    StartNodeSchema,
    MessageNodeSchema,
    ConditionNodeSchema,
    EndNodeSchema,
    NodeType,
)
from services.node import NodeService

router = APIRouter()
node_service = NodeService()

"""
Get exist node
"""


@router.get("/{node_id}/", tags=["nodes"], status_code=status.HTTP_200_OK)
async def get_node(node_id: int, db: Session = Depends(get_db)):
    return node_service.get_node(db=db, node_id=node_id)


"""
Create a new nodes
"""


@router.post(
    "/create-start-node/",
    tags=["nodes"],
    status_code=status.HTTP_201_CREATED,
)
def create_start_node(node_data: StartNodeSchema, db: Session = Depends(get_db)):
    return node_service.create_node(
        node_type=NodeType.start.value, db=db, node_data=node_data
    )


@router.post(
    "/create-message-node/", tags=["nodes"], status_code=status.HTTP_201_CREATED
)
def create_message_node(node_data: MessageNodeSchema, db: Session = Depends(get_db)):
    return node_service.create_node(
        node_type=NodeType.message.value, db=db, node_data=node_data
    )


@router.post(
    "/create-condition-node/", tags=["nodes"], status_code=status.HTTP_201_CREATED
)
def create_condition_node(
    node_data: ConditionNodeSchema, db: Session = Depends(get_db)
):
    return node_service.create_node(
        node_type=NodeType.condition.value, db=db, node_data=node_data
    )


@router.post("/create-end-node/", tags=["nodes"], status_code=status.HTTP_201_CREATED)
def create_end_node(node_data: EndNodeSchema, db: Session = Depends(get_db)):
    return node_service.create_node(
        node_type=NodeType.end.value, db=db, node_data=node_data
    )


"""
Edit an existing node
"""


@router.put(
    "/update-start-node/{node_id}/", tags=["nodes"], status_code=status.HTTP_200_OK
)
def update_start_node(
    node_id: int, node_data: StartNodeSchema, db: Session = Depends(get_db)
):
    return node_service.update_node(node_id=node_id, data=node_data, db=db)


@router.put(
    "/update-message-node/{node_id}/", tags=["nodes"], status_code=status.HTTP_200_OK
)
def update_message_node(
    node_id: int, node_data: MessageNodeSchema, db: Session = Depends(get_db)
):
    return node_service.update_node(node_id=node_id, data=node_data, db=db)


@router.put(
    "/update-condition-node/{node_id}/", tags=["nodes"], status_code=status.HTTP_200_OK
)
def update_condition_node(
    node_id: int, node_data: ConditionNodeSchema, db: Session = Depends(get_db)
):
    return node_service.update_node(node_id=node_id, data=node_data, db=db)


@router.put(
    "/update-end-node/{node_id}/", tags=["nodes"], status_code=status.HTTP_200_OK
)
def update_end_node(
    node_id: int, node_data: EndNodeSchema, db: Session = Depends(get_db)
):
    return node_service.update_node(node_id=node_id, data=node_data, db=db)


"""
Drop node
"""


@router.delete(
    "/node/{node_id}", tags=["nodes"], status_code=status.HTTP_204_NO_CONTENT
)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    return node_service.delete_node(node_id=node_id, db=db)
