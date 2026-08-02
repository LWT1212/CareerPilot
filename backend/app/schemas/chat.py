# 聊天相关的数据模型

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 创建聊天请求
class ChatCreate(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = "gpt-4"


# 聊天响应
class ChatResponse(BaseModel):
    id: str
    project_id: Optional[str]  # 全局聊天为 None
    title: Optional[str]
    model: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# 发送消息请求
class MessageCreate(BaseModel):
    content: str
    stream: bool = False


# 消息响应
class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    agent_used: Optional[str]
    tokens_used: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# 消息列表响应
class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    total: int
