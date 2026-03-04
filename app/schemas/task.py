from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    """Enum for task status"""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskBase(BaseModel):
    """Base Task schema with common attributes"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    tag_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="List of tag IDs to associate with the task"
    )


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated task title")
    description: Optional[str] = Field(None, description="Updated task description")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    tag_ids: Optional[List[int]] = Field(None, description="Updated list of tag IDs")


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    owner_id: int
    tags: List["TagResponseSimple"] = Field(default_factory=list, description="Associated tags")

    model_config = ConfigDict(from_attributes=True)


# Simple tag schema to avoid circular imports
class TagResponseSimple(BaseModel):
    """Simplified Tag schema for use in TaskResponse"""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# Update forward references
TaskResponse.model_rebuild()
