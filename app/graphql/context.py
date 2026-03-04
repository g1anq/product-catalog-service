from typing import Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends
from app.models.user import User
from app.core.security import verify_token
from app.repositories.user import UserRepository


from strawberry.fastapi import BaseContext

@dataclass
class GraphQLContext(BaseContext):
    request: Request
    db: AsyncSession
    current_user: Optional[User] = None


async def get_current_user_from_token(
    request: Request,
    db: AsyncSession
) -> Optional[User]:
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    # Extract token
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    # Verify token
    user_id_str = verify_token(token, token_type="access")
    if not user_id_str:
        return None
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        return None
    
    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    
    if not user or not user.is_active:
        return None
    
    return user


async def get_graphql_context(
    request: Request,
    db: AsyncSession
) -> GraphQLContext:
    current_user = await get_current_user_from_token(request, db)
    
    return GraphQLContext(
        request=request,
        db=db,
        current_user=current_user
    )
