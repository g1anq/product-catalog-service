from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.task import Task, TaskStatus
from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_owner(
        self,
        task_id: int,
        owner_id: int
    ) -> Optional[Task]:
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.tags))
            .where(and_(Task.id == task_id, Task.owner_id == owner_id))
        )
        return result.scalar_one_or_none()

    async def get_multi_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        query = select(Task).options(selectinload(Task.tags)).where(Task.owner_id == owner_id)
        
        if status:
            query = query.where(Task.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_task(
        self,
        owner_id: int,
        title: str,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        tag_ids: Optional[List[int]] = None
    ) -> Task:
        task_data = {
            "title": title,
            "description": description,
            "owner_id": owner_id,
            "status": status
        }
        task = await self.create(task_data)
        
        # Add tags if provided
        if tag_ids:
            await self.add_tags(task.id, owner_id, tag_ids)
            await self.db.refresh(task)
        
        return task

    async def update_task(
        self,
        task_id: int,
        owner_id: int,
        **kwargs
    ) -> Optional[Task]:
        # Verify ownership
        task = await self.get_by_owner(task_id, owner_id)
        if not task:
            return None
        
        # Remove tag_ids from kwargs as it needs special handling
        tag_ids = kwargs.pop("tag_ids", None)
        
        # Update task fields
        if kwargs:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            if update_data:
                await self.update(task_id, update_data)
        
        # Update tags if provided
        if tag_ids is not None:
            await self.set_tags(task_id, owner_id, tag_ids)
        
        # Refresh and return
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_id: int, owner_id: int) -> bool:
        task = await self.get_by_owner(task_id, owner_id)
        if not task:
            return False
        
        return await self.delete(task_id)

    async def add_tags(
        self,
        task_id: int,
        owner_id: int,
        tag_ids: List[int]
    ) -> Optional[Task]:
        task = await self.get_by_owner(task_id, owner_id)
        if not task:
            return None
        
        # Get tags
        result = await self.db.execute(
            select(Tag).where(Tag.id.in_(tag_ids))
        )
        tags = list(result.scalars().all())
        
        # Add tags that aren't already associated
        existing_tag_ids = {tag.id for tag in task.tags}
        for tag in tags:
            if tag.id not in existing_tag_ids:
                task.tags.append(tag)
        
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def remove_tags(
        self,
        task_id: int,
        owner_id: int,
        tag_ids: List[int]
    ) -> Optional[Task]:
        task = await self.get_by_owner(task_id, owner_id)
        if not task:
            return None
        
        # Remove tags
        task.tags = [tag for tag in task.tags if tag.id not in tag_ids]
        
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def set_tags(
        self,
        task_id: int,
        owner_id: int,
        tag_ids: List[int]
    ) -> Optional[Task]:
        task = await self.get_by_owner(task_id, owner_id)
        if not task:
            return None
        
        # Get tags
        result = await self.db.execute(
            select(Tag).where(Tag.id.in_(tag_ids))
        )
        tags = list(result.scalars().all())
        
        # Replace all tags
        task.tags = tags
        
        await self.db.commit()
        await self.db.refresh(task)
        return task
