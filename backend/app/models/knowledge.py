# 知识库模型

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base


class KnowledgeDocument(Base):
    """知识文档"""
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # project_id 为空 = 全局知识库文档
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, md, txt
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content = Column(Text, nullable=True)  # 提取的文本内容
    chunks = Column(JSON, nullable=True)  # 分块结果
    embedding_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    embedding_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="knowledge_documents")
