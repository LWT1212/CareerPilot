# 项目记忆模型 - 跨会话记住项目的关键信息

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class ProjectMemory(Base):
    """项目记忆：决策/进度/问题/偏好"""
    __tablename__ = "project_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    memory_type = Column(String(20), nullable=False)
    # decision(决策) / progress(进度) / problem(问题) / preference(偏好)
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=3)  # 重要度 1-5
    source_chat_id = Column(String(36), nullable=True)  # 来源聊天（追溯）
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", backref="project_memories")
