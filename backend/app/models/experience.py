# 经验模型

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base


class Experience(Base):
    """开发经验"""
    __tablename__ = "experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # bug, solution, architecture, lesson, note
    content = Column(Text, nullable=False)
    solution = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="experiences")
