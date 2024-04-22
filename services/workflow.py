import networkx as nx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database.models import (
    Workflow,
    StartNode,
    MessageNode,
    ConditionNode,
    EndNode,
    NodeType,
)
from schemas import workflow
from services.utils import get_object_by_id, save_object, delete_object


class WorkflowGraph:
    """
    A class to represent a workflow graph.

    Attributes:
    - workflow_id (int): The ID of the workflow.
    - db (Session): The database session.
    - G (nx.DiGraph): The graph representing the workflow.
    - start_node: The starting node of the workflow.
    - end_node: The ending node of the workflow.
    """

    def __init__(self, workflow_id: int, db: Session):
        self.workflow_id = workflow_id
        self.db: Session = db
        self.G = nx.DiGraph()
        self.start_node = None
        self.end_node = None

    def _add_node(self, node: StartNode | EndNode | MessageNode | ConditionNode):
        """Add a node to the graph."""
        self.G.add_node(node)

    def _add_edge(self, source_node_id: int, target_node_id: int):
        """
        Add an edge to the graph.
        """
        self.G.add_edge(source_node_id, target_node_id)

    def _validate_workflow(self, workflow: Workflow):
        """
        Validate the existence of the workflow.
        """
        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    def _validate_last_node(self):
        """
        Validate the existence of the last node.
        """
        if not self.last_node:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def _validate_reachable_nodes(self):
        """
        Validate reachable nodes in the graph.
        """
        reachable_nodes = nx.bfs_tree(self.G, source=self.start_node).nodes()
        if self.last_node not in reachable_nodes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def _validate_edges(self):
        """Validate the existence of edges in the graph."""
        if not self.G.edges:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def create_graph(self) -> None:
        """
        Create the workflow graph.
        """
        workflow = get_object_by_id(
            model=Workflow, object_id=self.workflow_id, db_session=self.db
        )
        self._validate_workflow(workflow)
        for node in workflow.nodes:
            self._add_node(node)
            if isinstance(node, StartNode):
                if node.next_node.node_type != NodeType.condition.value:
                    self._add_edge(node.id, node.next_node_id)
                    self.start_node = node.id
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Condition node could be reached only through message node or condition node",
                    )
            elif isinstance(node, MessageNode):
                if node.next_node.node_type != NodeType.start.value:
                    self._add_edge(node.id, node.next_node_id)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Start node could not have any previous nodes",
                    )
            elif isinstance(node, ConditionNode):
                self._add_edge(node.id, node.yes_node_id)
                self._add_edge(node.id, node.no_node_id)
            elif isinstance(node, EndNode):
                self.last_node = node.id

        self._validate_last_node()
        self._validate_reachable_nodes()
        self._validate_edges()

    def run_graph(self) -> dict:
        """
        Run the workflow graph.

        Returns:
        - dict: A dictionary containing the path and edges of the graph.
        """
        """Run the workflow graph."""
        sequence = nx.shortest_path(self.G, target=self.last_node)[self.start_node]
        edges = list(self.G.edges)
        response_data = {
            "path": sequence,
            "edges": edges,
        }
        return response_data


class WorkflowServices:
    """
    A class to provide workflow services.
    """

    def create_workflow(
        self, workflow_data: workflow.WorkflowCreateSchema, db: Session
    ) -> Workflow:
        """
        Create a new workflow service
        :param workflow_data: Data for creating the workflow.
        :param db: Database session for the operation.
        :return: The created workflow.
        """
        new_workflow = Workflow(name=workflow_data.name)
        save_object(new_workflow, db)
        return new_workflow

    def get_workflow(self, workflow_id: int, db: Session) -> Workflow:
        """
        Retrieves a workflow by its ID.
        :param workflow_id: ID of the workflow to retrieve.
        :param db:
        :return:  The found workflow or False if workflow not found.
        """
        workflow = get_object_by_id(
            model=Workflow, object_id=workflow_id, db_session=db
        )
        return workflow

    def update_workflow(
        self,
        workflow_id: int,
        data: workflow.WorkflowUpdateSchema,
        db: Session,
    ) -> Workflow:
        """
        Updates a workflow.
        :param workflow_id: ID of the workflow to update.
        :param data: Data for updating the workflow.
        :param db:
        :return: The updated workflow or False if workflow not found.
        """
        workflow = get_object_by_id(
            model=Workflow, object_id=workflow_id, db_session=db
        )
        workflow.name = data.name
        save_object(workflow, db)
        return workflow

    def delete_workflow(self, workflow_id: int, db: Session) -> bool:
        """
        Delete a workflow
        :param workflow_id: ID of the workflow to delete.
        :param db: Database session for the operation.
        :return:  True if the workflow was deleted.
        """
        workflow = get_object_by_id(
            model=Workflow, object_id=workflow_id, db_session=db
        )
        delete_object(workflow, db)
        return True

    def create_and_run_sequence(self, workflow_id: int, db: Session):
        """Create and run the workflow sequence."""
        workflow_graph = WorkflowGraph(workflow_id, db)
        workflow_graph.create_graph()
        return workflow_graph.run_graph()
