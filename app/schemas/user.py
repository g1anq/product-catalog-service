from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base User schema with common attributes"""
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="User password (min 8 characters, max 72 bytes for bcrypt)"
    )


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=72,
        description="Updated password (min 8 characters, max 72 bytes for bcrypt)"
    )
    is_active: Optional[bool] = Field(None, description="Account active status")


class UserResponse(UserBase):
    """Schema for user response (public data)"""
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)"""
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
