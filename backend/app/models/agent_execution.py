# Agent执行记录模型

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base


class AgentExecution(Base):
    """Agent执行记录"""
    __tablename__ = "agent_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_type = Column(String(50), nullable=False)  # coordinator, knowledge(tool:xxx), ...
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String(20), default="success")  # success, failed
    created_at = Column(DateTime, default=datetime.utcnow)
