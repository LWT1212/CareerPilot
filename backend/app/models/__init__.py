# 导入所有模型
from app.models.user import User
from app.models.project import Project
from app.models.chat import Chat, Message
from app.models.knowledge import KnowledgeDocument
from app.models.experience import Experience
from app.models.interview import Interview, InterviewQuestion
from app.models.document import Document

__all__ = [
    "User", "Project", "Chat", "Message", "KnowledgeDocument",
    "Experience", "Interview", "InterviewQuestion", "Document"
]
