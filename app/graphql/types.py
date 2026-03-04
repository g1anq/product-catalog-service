import strawberry
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus as TaskStatusEnum
import strawberry
from enum import Enum


@strawberry.enum
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@strawberry.type
class User:
    id: int
    email: str
    is_active: bool
    created_at: datetime


@strawberry.type
class Tag:
    id: int
    name: str


@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    owner_id: int
    tags: List[Tag]


@strawberry.type
class TaskWithOwner:
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    owner_id: int
    owner: User
    tags: List[Tag]


@strawberry.input
class CreateTaskInput:
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    tag_ids: Optional[List[int]] = None


@strawberry.input
class UpdateTaskInput:
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    tag_ids: Optional[List[int]] = None


@strawberry.input
class AddTagToTaskInput:
    task_id: int
    tag_id: int
