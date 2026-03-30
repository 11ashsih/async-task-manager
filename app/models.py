from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str
