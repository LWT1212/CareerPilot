# 面试模型

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base


class Interview(Base):
    """面试记录"""
    __tablename__ = "interviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    company = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    interview_date = Column(Date, nullable=True)
    interviewer = Column(String(100), nullable=True)
    status = Column(String(20), default="completed")  # scheduled, completed, cancelled
    overall_feedback = Column(Text, nullable=True)
    result = Column(String(50), nullable=True)  # offer, rejected, pending, ghosted
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="interviews")
    questions = relationship("InterviewQuestion", backref="interview", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    """面试问题"""
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    interviewer_feedback = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Redis, 系统设计, 算法, 项目经验
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    rating = Column(Integer, nullable=True)  # 1-5
    learning_suggestion = Column(Text, nullable=True)
    is_weak_point = Column(Integer, default=0)  # 0=否, 1=是
    created_at = Column(DateTime, default=datetime.utcnow)
