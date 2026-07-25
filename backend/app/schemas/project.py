# 项目相关的数据模型（Schema）

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 创建项目请求
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


# 更新项目请求
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    status: Optional[str] = None


# 项目响应
class ProjectResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 项目列表响应
class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
