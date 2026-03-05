from typing import AsyncGenerator
from strawberry.fastapi import GraphQLRouter
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.schema import schema
from app.graphql.context import GraphQLContext, get_current_user_from_token
from app.api.deps import get_db


async def get_context(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> GraphQLContext:
    current_user = await get_current_user_from_token(request, db)
    
    return GraphQLContext(
        request=request,
        db=db,
        current_user=current_user
    )


# Create GraphQL router with context
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context
)
