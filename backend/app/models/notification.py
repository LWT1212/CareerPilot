# 提醒通知模型 - AI主动提醒（文档更新/知识库影响等）

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Notification(Base):
    """AI主动提醒"""
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    ntype = Column(String(30), nullable=False)
    # doc_update(文档更新提醒) / knowledge_impact(知识库影响) / weakness(薄弱点)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", backref="notifications")
