

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user, get_task_repository
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.models.user import User
from app.models.task import TaskStatus
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> Any:
    
    task = await task_repo.create_task(
        owner_id=current_user.id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        tag_ids=task_in.tag_ids
    )
    
    return task


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tasks to return"),
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> Any:
    
    tasks = await task_repo.get_multi_by_owner(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status_filter
    )
    
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> Any:
    
    task = await task_repo.get_by_owner(task_id, current_user.id)
    
    if not task:
        task_exists = await task_repo.exists(task_id)
        if task_exists:
            raise ForbiddenException(detail="You don't have permission to access this task")
        else:
            raise NotFoundException(detail="Task not found")
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> Any:
    
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException(detail="No fields to update")
    
    # Update task 
    task = await task_repo.update_task(
        task_id=task_id,
        owner_id=current_user.id,
        **update_data
    )
    
    if not task:
        task_exists = await task_repo.exists(task_id)
        if task_exists:
            raise ForbiddenException(detail="You don't have permission to modify this task")
        else:
            raise NotFoundException(detail="Task not found")
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> None:
    
    deleted = await task_repo.delete_task(task_id, current_user.id)
    
    if not deleted:
        task_exists = await task_repo.exists(task_id)
        if task_exists:
            raise ForbiddenException(detail="You don't have permission to delete this task")
        else:
            raise NotFoundException(detail="Task not found")


@router.post("/{task_id}/tags", response_model=TaskResponse)
async def add_tags_to_task(
    task_id: int,
    tag_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> Any:
    
    if not tag_ids:
        raise BadRequestException(detail="Tag IDs list cannot be empty")
    
    task = await task_repo.add_tags(task_id, current_user.id, tag_ids)
    
    if not task:
        task_exists = await task_repo.exists(task_id)
        if task_exists:
            raise ForbiddenException(detail="You don't have permission to modify this task")
        else:
            raise NotFoundException(detail="Task not found")
    
    return task


@router.delete("/{task_id}/tags", response_model=TaskResponse)
async def remove_tags_from_task(
    task_id: int,
    tag_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    task_repo: TaskRepository = Depends(get_task_repository)
) -> Any:
    
    if not tag_ids:
        raise BadRequestException(detail="Tag IDs list cannot be empty")
    
    task = await task_repo.remove_tags(task_id, current_user.id, tag_ids)
    
    if not task:
        task_exists = await task_repo.exists(task_id)
        if task_exists:
            raise ForbiddenException(detail="You don't have permission to modify this task")
        else:
            raise NotFoundException(detail="Task not found")
    
    return task
