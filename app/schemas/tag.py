from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class TagBase(BaseModel):
    """Base Tag schema with common attributes"""
    name: str = Field(..., min_length=1, max_length=100, description="Tag name")


class TagCreate(TagBase):
    """Schema for creating a new tag"""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated tag name")


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class TagWithTasks(TagResponse):
    """Schema for tag response with associated tasks"""
    tasks: List["TaskResponseSimple"] = Field(default_factory=list, description="Associated tasks")

    model_config = ConfigDict(from_attributes=True)


# Simple task schema to avoid circular imports
class TaskResponseSimple(BaseModel):
    """Simplified Task schema for use in TagWithTasks"""
    id: int
    title: str
    status: str

    model_config = ConfigDict(from_attributes=True)


# Update forward references
TagWithTasks.model_rebuild()
