# 经验相关的数据模型

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# 创建经验请求
class ExperienceCreate(BaseModel):
    title: str
    type: str  # bug, solution, architecture, lesson, note
    content: str
    solution: Optional[str] = None
    tags: List[str] = []


# 更新经验请求
class ExperienceUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    solution: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None


# 经验响应
class ExperienceResponse(BaseModel):
    id: str
    project_id: str
    title: str
    type: str
    content: str
    solution: Optional[str]
    tags: List[str]
    is_pinned: bool
    created_at: datetime

    class Config:
        from_attributes = True
