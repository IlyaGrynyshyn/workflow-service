# Workflow Management API

This project implements an API for managing workflows using the concept of graphs. The system allows creating four types of nodes and includes API development using FastAPI and Pydantic for handling web requests, integration with the networkX library for graph management, and implementation of an algorithm to determine the path from the initial to the final node.

## Overview

The API allows creating and managing workflows with different types of nodes: Start Node, Message Node, Condition Node, and End Node. Each type of node has its characteristics and limitations, which are defined below.

## Node Types

### Start Node:
- Can have only one outgoing edge.
- Cannot have incoming edges.

### Message Node:
- Has statuses: pending, sent, opened.
- Has a message text.
- Can have only one outgoing edge.
- Can have multiple incoming edges.

### Condition Node:
- Has two outgoing edges: Yes and No.
- The condition determines the path through the Yes or No edge.
- Can have multiple incoming edges.

### End Node:
- The final node for a workflow.
- Can have multiple incoming edges.
- Cannot have outgoing edges.

## Features

The API has the following functionality:

- Creating, updating, and deleting workflows.
- Creating nodes of different types.
- Node configuration: changing parameters or deleting nodes.
- Running Workflow: initializing and starting the selected Workflow, returning a detailed path from Start to End Node or an error if it is not possible to reach the final node.

## Technologies

- **FastAPI**: for building the API.
- **Pydantic**: for data validation.
- **networkX**: for graph construction.
- **SQLAlchemy** or **Tortoise ORM**: for working with the database.
- **Pytest**: for writing test cases and testing the algorithm and API.

## Usage Instructions

### 1. **Cloning the Repository:**

  - Clone the repository to your local machine `https://github.com/IlyaGrynyshyn/workflow-service`.
  - Create virtual environment `python3 -m venv venv`
  - Install the required dependencies using `pip install -r requirements.txt`.

2. **Running:**
    - Run with unicorn - 
    ```bash
    `uvicorn main:app`

3. **Running with Docker Compose**
    ```bash
    docker-compose up --build
   ```
   
## Running tests

   - Running tests for routers 
```bash
pytest tests/test_routers/
   ```
   - Running tests for services 
```bash
pytest tests/test_services/
   ```

## Documentation
API documentation is available at http://127.0.0.1:8000/docs/





