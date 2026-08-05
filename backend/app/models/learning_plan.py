# 学习计划模型 - AI检测薄弱点后自动生成

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class LearningPlan(Base):
    """AI自动生成的学习计划（针对面试薄弱点）"""
    __tablename__ = "learning_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    category = Column(String(100), nullable=False)  # 薄弱类别，如 Redis
    title = Column(String(200), nullable=False)     # 学习计划标题
    content = Column(Text, nullable=False)          # 计划内容（markdown）
    weak_count = Column(Integer, default=0)         # 薄弱次数
    status = Column(String(20), default="active")   # active, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", backref="learning_plans")
