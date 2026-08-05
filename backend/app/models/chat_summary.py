# 对话摘要模型 - 旧对话压缩摘要，跨会话回顾

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class ChatSummary(Base):
    """对话摘要"""
    __tablename__ = "chat_summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    summary = Column(Text, nullable=False)  # LLM生成的摘要
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", backref="summaries")
