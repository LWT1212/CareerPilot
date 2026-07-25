# 知识库相关的数据模型

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# 知识文档响应
class KnowledgeDocumentResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_type: str
    file_size: Optional[int]
    embedding_status: str
    embedding_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# 知识检索请求
class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5


# 知识检索结果
class KnowledgeSearchResult(BaseModel):
    document_id: str
    filename: str
    content: str
    score: float
    metadata: Optional[dict] = None


# 知识检索响应
class KnowledgeSearchResponse(BaseModel):
    results: List[KnowledgeSearchResult]
    query: str
    total_results: int
