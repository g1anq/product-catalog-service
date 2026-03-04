from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.task_tag import task_tag_association


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    tasks = relationship(
        "Task",
        secondary=task_tag_association,
        back_populates="tags"
    )
