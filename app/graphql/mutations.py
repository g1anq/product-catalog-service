import strawberry
from typing import Optional
from strawberry.types import Info

from app.graphql.types import Task, CreateTaskInput, UpdateTaskInput, AddTagToTaskInput, Tag 
from app.graphql.context import GraphQLContext
from app.graphql.queries import require_authentication, convert_task_to_graphql
from app.repositories.task import TaskRepository
from app.repositories.tag import TagRepository
from app.models.task import TaskStatus as TaskStatusEnum


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_task(
        self,
        info: Info,
        input: CreateTaskInput
    ) -> Task:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Convert GraphQL status to model enum
        status = TaskStatusEnum.TODO
        if input.status:
            status = TaskStatusEnum[input.status.value]
        
        # Create task
        task = await task_repo.create_task(
            owner_id=current_user.id,
            title=input.title,
            description=input.description,
            status=status,
            tag_ids=input.tag_ids or []
        )
        
        return convert_task_to_graphql(task)
    
    @strawberry.mutation
    async def update_task(
        self,
        info: Info,
        task_id: int,
        input: UpdateTaskInput
    ) -> Optional[Task]:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Prepare update data
        update_data = {}
        
        if input.title is not None:
            update_data["title"] = input.title
        
        if input.description is not None:
            update_data["description"] = input.description
        
        if input.status is not None:
            update_data["status"] = TaskStatusEnum[input.status.value]
        
        if input.tag_ids is not None:
            update_data["tag_ids"] = input.tag_ids
        
        # Check if there's anything to update
        if not update_data:
            # Just return the existing task
            task = await task_repo.get_by_owner(task_id, current_user.id)
            if not task:
                raise Exception("Task not found or you don't have permission to access it")
            return convert_task_to_graphql(task)
        
        # Update task 
        task = await task_repo.update_task(
            task_id=task_id,
            owner_id=current_user.id,
            **update_data
        )
        
        if not task:
            raise Exception("Task not found or you don't have permission to update it")
        
        return convert_task_to_graphql(task)
    
    @strawberry.mutation
    async def delete_task(
        self,
        info: Info,
        task_id: int
    ) -> bool:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Delete task 
        deleted = await task_repo.delete_task(task_id, current_user.id)
        
        if not deleted:
            raise Exception("Task not found or you don't have permission to delete it")
        
        return True
    
    @strawberry.mutation
    async def add_tag_to_task(
        self,
        info: Info,
        input: AddTagToTaskInput
    ) -> Task:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Add tag to task 
        task = await task_repo.add_tags(
            task_id=input.task_id,
            owner_id=current_user.id,
            tag_ids=[input.tag_id]
        )
        
        if not task:
            raise Exception("Task not found or you don't have permission to modify it")
        
        return convert_task_to_graphql(task)
    
    @strawberry.mutation
    async def remove_tag_from_task(
        self,
        info: Info,
        task_id: int,
        tag_id: int
    ) -> Task:
        # Require authentication
        current_user = require_authentication(info)
        
        context: GraphQLContext = info.context
        task_repo = TaskRepository(context.db)
        
        # Remove tag from task 
        task = await task_repo.remove_tags(
            task_id=task_id,
            owner_id=current_user.id,
            tag_ids=[tag_id]
        )
        
        if not task:
            raise Exception("Task not found or you don't have permission to modify it")
        
        return convert_task_to_graphql(task)
    
    @strawberry.mutation
    async def create_tag(
        self,
        info: Info,
        name: str
    ) -> Tag:
        # Require authentication
        require_authentication(info)
        
        context: GraphQLContext = info.context
        tag_repo = TagRepository(context.db)
        
        # Check if tag already exists
        existing_tag = await tag_repo.get_by_name(name)
        if existing_tag:
            raise Exception(f"Tag '{name}' already exists")
        
        # Create tag
        tag = await tag_repo.create({"name": name})
        
        from app.graphql.queries import convert_tag_to_graphql
        return convert_tag_to_graphql(tag)
