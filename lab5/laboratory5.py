from fastapi import FastAPI, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field, conint
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

# Get the API key securely from environment variables
API_KEY = os.getenv("API_KEY")

app = FastAPI()

task_db: List[dict] = [
    {"task_id": 1, "task_title": "Laboratory Activity", "task_desc": "Create Lab Act 2", "is_finished": False}
]

tasks = [{"id": 1, "name": "Task 1", "description": "Description 1"},
         {"id": 2, "name": "Task 2", "description": "Description 2"}]


class TaskV2(BaseModel):
    name: str = Field(..., example="Task 1")
    description: str = Field(..., example="Description of Task 1") 

class TaskV1(BaseModel):
    task_id: conint(gt=0) 
    task_title: str = Field(..., min_length=1) 
    task_desc: str = Field(default="", max_length=255)  
    is_finished: bool = Field(default=False)  

def check_api_key(api_key: str = None):
    if api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return True


# Version 1 Endpoints
@app.post("/v1/tasks")
def add_task_v1(task: TaskV1):
    """Add Task (Version 1)."""
    if any(t['task_id'] == task.task_id for t in task_db):
        return {"error": "Task ID already exists"}
    task_db.append(task.dict())
    return {"status": "ok"}
    

@app.get("/v1/tasks/{task_id}")
def get_task_v1(task_id: int):
    """Retrieve a specific task by task_id (Version 1)."""
    for task in task_db:
        if task["task_id"] == task_id:
            return {"status": "ok", "result": task}
    return {"error": "Task not found"}


@app.patch("/v1/tasks/{task_id}")
def update_task_v1(task_id: int, updated_task: TaskV1):
    """Update an existing task's details (Version 1)."""
    for idx, task in enumerate(task_db):
        if task["task_id"] == task_id:
            task_db[idx].update(updated_task.dict(exclude_unset=True))
            return {"status": "ok", "updated_data": task_db[idx]}
    return {"error": "Task not found. Cannot update record"}

@app.delete("/v1/tasks/{task_id}")
def delete_task_v1(task_id: int):
    """Delete a task by task_id (Version 1)."""
    for idx, task in enumerate(task_db):
        if task["task_id"] == task_id:
            removed_task = task_db.pop(idx)
            return {"status": "ok", "removed_data": removed_task}
    return {"error": "Task not found. Cannot delete record"}


# Version 2 Endpoints

@app.post("/v2/tasks", status_code=status.HTTP_201_CREATED)
async def add_task_v2(task: TaskV2, api_key: str = Depends(check_api_key)):
    """Add a new task (Version 2)."""
    task_data = task.dict()  
    task_data["id"] = len(tasks) + 1  
    tasks.append(task_data) 
    return task_data 

@app.get("/v2/tasks/{task_id}", response_model=dict)
async def get_task_v2(task_id: int, api_key: str = Depends(check_api_key)):
    """Retrieve a specific task by ID (Version 2)."""
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.put("/v2/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task_v2(task_id: int, updated_task: TaskV2, api_key: str = Depends(check_api_key)):
    """Update an existing task (Version 2)."""
    
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task["name"] = updated_task.name
    task["description"] = updated_task.description
    return None


@app.delete("/v2/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_v2(task_id: int, api_key: str = Depends(check_api_key)):
    """Delete a task by ID (Version 2)."""
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    tasks.remove(task)