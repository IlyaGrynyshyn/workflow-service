from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from schemas.workflow import WorkflowCreateSchema, WorkflowUpdateSchema
from services.workflow import WorkflowServices

router = APIRouter()

workflows_services = WorkflowServices()


@router.post("/create/", status_code=status.HTTP_201_CREATED, tags=["workflows"])
def create_workflow(workflow_data: WorkflowCreateSchema, db: Session = Depends(get_db)):
    return workflows_services.create_workflow(workflow_data=workflow_data, db=db)


@router.get("/get/{workflow_id}/", status_code=status.HTTP_200_OK, tags=["workflows"])
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = workflows_services.get_workflow(workflow_id=workflow_id, db=db)
    if workflow:
        return workflow
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.put(
    "/update/{workflow_id}/", status_code=status.HTTP_200_OK, tags=["workflows"]
)
def update_workflow(
    workflow_id: int, data: WorkflowUpdateSchema, db: Session = Depends(get_db)
):
    update_workflow = workflows_services.update_workflow(
        workflow_id=workflow_id, data=data, db=db
    )
    if not update_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return update_workflow


@router.delete(
    "/delete/{workflow_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["workflows"]
)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflows_services.delete_workflow(workflow_id=workflow_id, db=db)
    return {"message": "Workflow deleted"}, status.HTTP_204_NO_CONTENT


@router.post("/run-sequence/{workflow_id}", tags=["workflows"])
def run_sequence(workflow_id: int, db: Session = Depends(get_db)):
    return workflows_services.create_and_run_graph(db=db, workflow_id=workflow_id)
