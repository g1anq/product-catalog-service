

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.core.exceptions import BadRequestException, ConflictException
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    
    user_repo = UserRepository(db)
    
    # Check if user already exists
    existing_user = await user_repo.get_by_email(user_in.email)
    if existing_user:
        raise ConflictException(detail="Email already registered")
    
    # Create new user
    user = await user_repo.create_user(
        email=user_in.email,
        password=user_in.password
    )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    
    user_repo = UserRepository(db)
    
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException(detail="No fields to update")
    
    if user_update.email and user_update.email != current_user.email:
        existing_user = await user_repo.get_by_email(user_update.email)
        if existing_user:
            raise ConflictException(detail="Email already registered")
    
    if user_update.password:
        await user_repo.update_password(current_user.id, user_update.password)
        update_data.pop("password", None)
    
    if update_data:
        updated_user = await user_repo.update(current_user.id, update_data)
    else:
        updated_user = await user_repo.get(current_user.id)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user
