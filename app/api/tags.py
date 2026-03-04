

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user, get_tag_repository
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.user import User
from app.repositories.tag import TagRepository
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagWithTasks

router = APIRouter()


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    current_user: User = Depends(get_current_active_user),
    tag_repo: TagRepository = Depends(get_tag_repository)
) -> Any:
    # Check if tag already exists
    existing_tag = await tag_repo.get_by_name(tag_in.name)
    if existing_tag:
        raise ConflictException(detail=f"Tag '{tag_in.name}' already exists")
    
    tag = await tag_repo.create({"name": tag_in.name})
    return tag


@router.get("", response_model=List[TagResponse])
async def list_tags(
    search: Optional[str] = Query(None, description="Search tags by name"),
    skip: int = Query(0, ge=0, description="Number of tags to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tags to return"),
    current_user: User = Depends(get_current_active_user),
    tag_repo: TagRepository = Depends(get_tag_repository)
) -> Any:
    if search:
        tags = await tag_repo.search_by_name(search, skip=skip, limit=limit)
    else:
        tags = await tag_repo.get_multi(skip=skip, limit=limit)
    
    return tags


@router.get("/{tag_id}", response_model=TagWithTasks)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    tag_repo: TagRepository = Depends(get_tag_repository)
) -> Any:
    tag = await tag_repo.get_with_tasks(tag_id)
    
    if not tag:
        raise NotFoundException(detail="Tag not found")
    
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    tag_repo: TagRepository = Depends(get_tag_repository)
) -> Any:
    tag = await tag_repo.get(tag_id)
    if not tag:
        raise NotFoundException(detail="Tag not found")
    
    update_data = tag_update.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException(detail="No fields to update")
    
    if tag_update.name and tag_update.name != tag.name:
        existing_tag = await tag_repo.get_by_name(tag_update.name)
        if existing_tag:
            raise ConflictException(detail=f"Tag '{tag_update.name}' already exists")
    
    updated_tag = await tag_repo.update(tag_id, update_data)
    
    if not updated_tag:
        raise NotFoundException(detail="Tag not found")
    
    return updated_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    tag_repo: TagRepository = Depends(get_tag_repository)
) -> None:
    deleted = await tag_repo.delete(tag_id)
    
    if not deleted:
        raise NotFoundException(detail="Tag not found")
