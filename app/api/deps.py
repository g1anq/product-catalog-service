from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.models.user import User
from app.repositories.user import UserRepository

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify and decode token
    user_id_str = verify_token(token, token_type="access")
    if not user_id_str:
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(db)


async def get_task_repository(
    db: AsyncSession = Depends(get_db)
):
    from app.repositories.task import TaskRepository
    return TaskRepository(db)


async def get_tag_repository(
    db: AsyncSession = Depends(get_db)
):
    from app.repositories.tag import TagRepository
    return TagRepository(db)
