# 知识库服务 - 处理文档上传、索引（RAG）、检索

import os
import uuid
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import KnowledgeSearchResult
from app.config import settings
from app.services.rag_service import (
    index_document,
    delete_document_vectors,
    search_documents,
    parse_document,
)


# 上传文档（project_id 为空 = 全局知识库）
def upload_document(db: Session, project_id, filename: str, file_content: bytes, file_type: str):
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
        project_id=project_id,  # 可为空（全局）
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        file_size=len(file_content),
        embedding_status="processing"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 索引文档：解析 → 分块 → 嵌入 → 存入ChromaDB
    # 全局文档用 "global" 作为集合名
    collection_key = project_id or "global"
    try:
        chunk_count = index_document(collection_key, new_doc.id, file_path, file_type)
        new_doc.embedding_status = "completed"
        new_doc.embedding_count = chunk_count
        # 保存解析后的纯文本
        new_doc.content = parse_document(file_path, file_type)[:5000]
        db.commit()
    except Exception as e:
        print(f"文档索引失败: {e}")
        new_doc.embedding_status = "failed"
        db.commit()

    db.refresh(new_doc)
    return new_doc


# 获取文档列表（project_id 为空 = 全局文档）
def get_documents(db: Session, project_id, skip: int = 0, limit: int = 20):
    if project_id:
        query = db.query(KnowledgeDocument).filter(KnowledgeDocument.project_id == project_id)
    else:
        query = db.query(KnowledgeDocument).filter(KnowledgeDocument.project_id.is_(None))
    docs = query.offset(skip).limit(limit).all()
    total = query.count()
    return docs, total


# 获取单个文档（全局文档也可访问）
def get_document(db: Session, doc_id: str, project_id=None):
    query = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id)
    if project_id:
        query = query.filter(KnowledgeDocument.project_id == project_id)
    return query.first()


# 删除文档（同时删除向量）
def delete_document(db: Session, doc_id: str, project_id=None):
    query = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id)
    if project_id:
        query = query.filter(KnowledgeDocument.project_id == project_id)
    doc = query.first()
    if not doc:
        return False

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # 删除ChromaDB中的向量
    collection_key = doc.project_id or "global"
    delete_document_vectors(collection_key, doc_id)

    db.delete(doc)
    db.commit()
    return True


# 知识检索（语义检索，基于ChromaDB；全局检索用 "global" 集合）
def search_knowledge(db: Session, project_id, query: str, top_k: int = 5):
    collection_key = project_id or "global"
    results = search_documents(collection_key, query, top_k)

    # 补充文档文件名信息
    output = []
    for r in results:
        doc = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == r["doc_id"]
        ).first()
        output.append(KnowledgeSearchResult(
            document_id=r["doc_id"],
            filename=doc.filename if doc else "未知",
            content=r["content"],
            score=r["score"],
            metadata={"file_type": doc.file_type if doc else ""}
        ))
    return output
