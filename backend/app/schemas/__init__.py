# 导入所有Schema
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse, MessageListResponse
from app.schemas.knowledge import (
    KnowledgeDocumentResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeSearchResponse
)

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "TokenResponse",
    "ProjectCreate", "ProjectUpdate", "ProjectResponse", "ProjectListResponse",
    "ChatCreate", "ChatResponse", "MessageCreate", "MessageResponse", "MessageListResponse",
    "KnowledgeDocumentResponse", "KnowledgeSearchRequest", "KnowledgeSearchResult", "KnowledgeSearchResponse"
]
