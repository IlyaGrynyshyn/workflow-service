import uvicorn
from fastapi import FastAPI

from database.config import Base, engine
from routers import workflow, node

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(workflow.router, prefix="/workflow")
app.include_router(node.router, prefix="/node")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
