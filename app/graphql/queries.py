import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.graphql.types import User, Task, Tag, TaskWithOwner
from app.graphql.context import GraphQLContext
from app.repositories.user import UserRepository
from app.repositories.task import TaskRepository
from app.repositories.tag import TagRepository
from app.models.user import User as UserModel
from app.models.task import Task as TaskModel
from app.models.tag import Tag as TagModel


def require_authentication(info: Info) -> UserModel:
    context: GraphQLContext = info.context
    if not context.current_user:
        raise Exception("Authentication required")
    return context.current_user


def convert_user_to_graphql(user: UserModel) -> User:
    """Convert SQLAlchemy User model to GraphQL User type"""
    return User(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at
    )


def convert_tag_to_graphql(tag: TagModel) -> Tag:
    """Convert SQLAlchemy Tag model to GraphQL Tag type"""
    return Tag(
        id=tag.id,
        name=tag.name
    )


def convert_task_to_graphql(task: TaskModel) -> Task:
    """Convert SQLAlchemy Task model to GraphQL Task type"""
    return Task(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        owner_id=task.owner_id,
        tags=[convert_tag_to_graphql(tag) for tag in task.tags]
    )


def convert_task_to_graphql_with_owner(task: TaskModel) -> TaskWithOwner:
    """Convert SQLAlchemy Task model to GraphQL TaskWithOwner type"""
    return TaskWithOwner(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        owner_id=task.owner_id,
        owner=convert_user_to_graphql(task.owner),
        tags=[convert_tag_to_graphql(tag) for tag in task.tags]
    )


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> List[User]:
        # Require authentication
        require_authentication(info)
        
        context: GraphQLContext = info.context
        user_repo = UserRepository(context.db)
        
        # Get all users
        users = await user_repo.get_multi(skip=0, limit=1000)
        
        return [convert_user_to_graphql(user) for user in users]
    
    @strawberry.field
    async def tasks(
        self,
        info: Info,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Parse status filter
        status_filter = None
        if status:
            from app.models.task import TaskStatus as TaskStatusEnum
            try:
                status_filter = TaskStatusEnum[status]
            except KeyError:
                raise Exception(f"Invalid status: {status}")
        
        # Get tasks with optimized loading 
        tasks = await task_repo.get_multi_by_owner(
            owner_id=current_user.id,
            skip=0,
            limit=limit,
            status=status_filter
        )
        
        return [convert_task_to_graphql(task) for task in tasks]
    
    @strawberry.field
    async def tasks_by_tag(
        self,
        info: Info,
        tag_name: str,
        limit: int = 100
    ) -> List[Task]:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        
        # Find tag by name
        tag_repo = TagRepository(context.db)
        tag = await tag_repo.get_by_name(tag_name)
        
        if not tag:
            return []
        
        stmt = (
            select(TaskModel)
            .options(selectinload(TaskModel.tags))
            .join(TaskModel.tags)
            .where(TaskModel.owner_id == current_user.id)
            .where(TagModel.id == tag.id)
            .limit(limit)
        )
        
        result = await context.db.execute(stmt)
        tasks = list(result.scalars().all())
        
        return [convert_task_to_graphql(task) for task in tasks]
    
    @strawberry.field
    async def task(
        self,
        info: Info,
        task_id: int
    ) -> Optional[Task]:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Get task 
        task = await task_repo.get_by_owner(task_id, current_user.id)
        
        if not task:
            return None
        
        return convert_task_to_graphql(task)
    
    @strawberry.field
    async def tags(self, info: Info) -> List[Tag]:
        # Require authentication
        require_authentication(info)
        
        context: GraphQLContext = info.context
        tag_repo = TagRepository(context.db)
        
        # Get all tags
        tags = await tag_repo.get_multi(skip=0, limit=1000)
        
        return [convert_tag_to_graphql(tag) for tag in tags]
    
    @strawberry.field
    async def me(self, info: Info) -> User:
        # Require authentication
        current_user = require_authentication(info)
        
        return convert_user_to_graphql(current_user)
