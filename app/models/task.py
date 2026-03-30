"""Pydantic models for tasks."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255, description="Task title")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New task title")
    completed: Optional[bool] = Field(None, description="Completion status")


class Task(BaseModel):
    """Full task representation stored in the database."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique task identifier")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    completed: bool = Field(default=False, description="Whether the task is completed")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of task creation",
    )

    @field_serializer("created_at")
    def serialise_created_at(self, value: datetime) -> str:
        """Serialise created_at as an ISO-8601 string.

        Args:
            value: The datetime value to serialise.

        Returns:
            ISO-8601 formatted string.
        """
        return value.isoformat()
