# 文档模型 - AI自动生成的项目文档

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Document(Base):
    """项目文档"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # readme, prd, star, resume, project_intro
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    change_reason = Column(Text, nullable=True)
    is_auto_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="documents")
