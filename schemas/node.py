from enum import Enum

from pydantic import BaseModel


class NodeType(str, Enum):
    start = "start"
    message = "message"
    condition = "condition"
    end = "end"


class NodeStatus(str, Enum):
    open = "Open"
    sent = "Sent"
    pending = "Pending"


class NodeBaseSchema(BaseModel):
    workflow_id: int

    class Config:
        from_attributes = True


class StartNodeSchema(NodeBaseSchema):
    next_node_id: int


class MessageNodeSchema(NodeBaseSchema):
    message: str
    status: NodeStatus
    next_node_id: int


class ConditionNodeSchema(NodeBaseSchema):
    condition: str
    yes_node_id: int
    no_node_id: int


class EndNodeSchema(NodeBaseSchema):
    pass
