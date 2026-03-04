from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository
from app.core.security import get_password_hash


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password: str) -> User:
        hashed_password = get_password_hash(password)
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "is_active": True
        }
        return await self.create(user_data)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        from app.core.security import verify_password
        
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        return user.is_active

    async def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        hashed_password = get_password_hash(new_password)
        return await self.update(user_id, {"hashed_password": hashed_password})
