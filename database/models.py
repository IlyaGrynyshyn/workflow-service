from sqlalchemy import Enum, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.config import Base
from schemas.node import NodeType, NodeStatus


class Workflow(Base):
    """Workflow model configuration."""

    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    nodes = relationship("Node", back_populates="workflow", cascade="all, delete")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(Enum(NodeType))
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    workflow = relationship("Workflow", back_populates="nodes", cascade="all, delete")

    __mapper_args__ = {"polymorphic_on": node_type}


""" Specific nodes classes """


class StartNode(Node):
    __tablename__ = "start_nodes"

    id = Column(Integer, ForeignKey("nodes.id"), primary_key=True, index=True)
    next_node_id = Column(Integer, ForeignKey("nodes.id"))
    next_node = relationship("Node", foreign_keys=next_node_id)

    __mapper_args__ = {
        "inherit_condition": id == Node.id,
        "polymorphic_identity": "start",
    }


class MessageNode(Node):
    __tablename__ = "message_nodes"
    id = Column(Integer, ForeignKey("nodes.id"), primary_key=True, index=True)
    status = Column(Enum(NodeStatus))
    message = Column(String)
    next_node_id = Column(Integer, ForeignKey("nodes.id"))
    next_node = relationship("Node", foreign_keys=next_node_id)
    __mapper_args__ = {
        "inherit_condition": id == Node.id,
        "polymorphic_identity": "message",
    }


class ConditionNode(Node):
    __tablename__ = "condition_nodes"
    id = Column(Integer, ForeignKey("nodes.id"), primary_key=True, index=True)
    condition = Column(String)
    yes_node_id = Column(Integer, ForeignKey("nodes.id"))
    no_node_id = Column(Integer, ForeignKey("nodes.id"))
    yes_node = relationship("Node", foreign_keys=yes_node_id)
    no_node = relationship("Node", foreign_keys=no_node_id)

    __mapper_args__ = {
        "inherit_condition": id == Node.id,
        "polymorphic_identity": "condition",
    }


class EndNode(Node):
    __tablename__ = "end_nodes"
    id = Column(Integer, ForeignKey("nodes.id"), primary_key=True, index=True)

    __mapper_args__ = {
        "inherit_condition": id == Node.id,
        "polymorphic_identity": "end",
    }
