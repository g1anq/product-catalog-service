from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.task_tag import task_tag_association
import enum


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        SQLEnum(TaskStatus, name="task_status", create_constraint=True),
        default=TaskStatus.TODO,
        nullable=False
    )

    # Relationships
    owner = relationship("User", back_populates="tasks")
    tags = relationship(
        "Tag",
        secondary=task_tag_association,
        back_populates="tasks"
    )
