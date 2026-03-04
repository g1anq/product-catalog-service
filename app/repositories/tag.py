from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tag, db)

    async def get_by_name(self, name: str) -> Optional[Tag]:
        result = await self.db.execute(
            select(Tag).where(Tag.name == name)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str) -> Tag:
        tag = await self.get_by_name(name)
        if tag:
            return tag
        
        return await self.create({"name": name})

    async def get_with_tasks(self, tag_id: int) -> Optional[Tag]:
        result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.tasks))
            .where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()

    async def get_all_with_tasks(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tag]:
        result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.tasks))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_name(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tag]:
        result = await self.db.execute(
            select(Tag)
            .where(Tag.name.ilike(f"%{search_term}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
