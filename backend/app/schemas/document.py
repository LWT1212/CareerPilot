# 文档相关的数据模型

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 文档响应
class DocumentResponse(BaseModel):
    id: str
    project_id: str
    doc_type: str
    title: Optional[str]
    content: Optional[str]
    version: int
    change_reason: Optional[str]
    is_auto_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 更新文档请求
class DocumentUpdate(BaseModel):
    content: str
    change_reason: Optional[str] = None


# 生成文档请求
class DocumentGenerateRequest(BaseModel):
    instruction: Optional[str] = None
