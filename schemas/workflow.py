from pydantic import BaseModel


class Workflow(BaseModel):
    """
    Model representing a workflow.
    """

    id: int
    name: str

    class Config:
        from_attributes = True


class WorkflowCreateSchema(BaseModel):
    """
    Schema for creating a new workflow.
    """

    name: str

    class Config:
        from_attributes = True


class WorkflowUpdateSchema(WorkflowCreateSchema):
    """
    Schema for updating an existing workflow.
    """

    pass
