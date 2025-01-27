                            #LABORATORY Activity 2: Working with HTTP actions and API parameters
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, conint
from typing import Optional, List
app = FastAPI()

class Task(BaseModel):
    task_id: conint(gt=0) 
    task_title: str = Field(..., min_length=1)  
    task_desc: str = Field(default="", max_length=255)  
    is_finished: bool = Field(default=False) 

task_db: List[dict] = [
    {"task_id": 1, "task_title": "Laboratory Activity", "task_desc": "Create Lab Act 2", "is_finished": False}
]


# GET implementation
@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    """Retrieve a specific task by task_id."""
    for task in task_db:
        if task["task_id"] == task_id:
            return {"status": "ok", "result": task}
    
    return {"error": "Task not found"}


# POST implementation
@app.post("/tasks")
def create_task(task: Task):
    """Create a new task."""
    if any(t['task_id'] == task.task_id for t in task_db):
        return {"error": "Task ID already exists"}
    
    task_db.append(task.dict())
    return {"status": "ok"}


# PATCH implementation
@app.patch("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    """Update an existing task's details."""
    for idx, task in enumerate(task_db):
        if task["task_id"] == task_id:
            # Update only the fields that are provided
            task_db[idx].update(updated_task.dict(exclude_unset=True))
            return {"status": "ok", "updated_data": task_db[idx]}
    
    return {"error": "Task not found. Cannot update record"}

# DELETE implementation
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task by task_id."""
    for idx, task in enumerate(task_db):
        if task["task_id"] == task_id:
            removed_task = task_db.pop(idx)
            return {"status": "ok", "removed_data": removed_task}
    
    return {"error": "Task not found. Cannot delete record"}

