# 知识库服务 - 处理文档上传、解析、检索

import os
import uuid
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import KnowledgeSearchRequest, KnowledgeSearchResult
from app.config import settings


# 上传文档
def upload_document(db: Session, project_id: str, filename: str, file_content: bytes, file_type: str):
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(filename)[1]
    saved_filename = f"{file_id}{file_ext}"

    # 保存文件
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 创建数据库记录
    new_doc = KnowledgeDocument(
        project_id=project_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        file_size=len(file_content),
        embedding_status="pending"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # TODO: 异步处理文档解析和向量嵌入
    # process_document.delay(new_doc.id)

    return new_doc


# 获取文档列表
def get_documents(db: Session, project_id: str, skip: int = 0, limit: int = 20):
    docs = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.project_id == project_id
    ).offset(skip).limit(limit).all()
    total = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.project_id == project_id
    ).count()
    return docs, total


# 获取单个文档
def get_document(db: Session, doc_id: str, project_id: str):
    return db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.project_id == project_id
    ).first()


# 删除文档
def delete_document(db: Session, doc_id: str, project_id: str):
    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.project_id == project_id
    ).first()
    if not doc:
        return False

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return True


# 知识检索（简单实现，后续可以接入ChromaDB）
def search_knowledge(db: Session, project_id: str, query: str, top_k: int = 5):
    # 获取该项目所有已完成嵌入的文档
    docs = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.project_id == project_id,
        KnowledgeDocument.embedding_status == "completed"
    ).all()

    results = []
    for doc in docs:
        # 简单的关键词匹配（后续替换为向量检索）
        if doc.content and query.lower() in doc.content.lower():
            results.append(KnowledgeSearchResult(
                document_id=doc.id,
                filename=doc.filename,
                content=doc.content[:500],  # 截取前500字符
                score=0.8,  # 模拟相似度
                metadata={"file_type": doc.file_type}
            ))

    return results[:top_k]
