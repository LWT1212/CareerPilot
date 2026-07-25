# 聊天和消息模型

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base


class Chat(Base):
    """聊天会话"""
    __tablename__ = "chats"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=True)
    model = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="chats")
    messages = relationship("Message", backref="chat", order_by="Message.created_at")


class Message(Base):
    """消息"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    extra_data = Column(JSON, nullable=True)  # 改名：metadata -> extra_data
    created_at = Column(DateTime, default=datetime.utcnow)
