# 文档服务

from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentUpdate


# 获取文档列表
def get_documents(db: Session, project_id: str):
    return db.query(Document).filter(Document.project_id == project_id).all()


# 获取单个文档
def get_document(db: Session, project_id: str, doc_type: str):
    return db.query(Document).filter(
        Document.project_id == project_id,
        Document.doc_type == doc_type
    ).first()


# 创建或更新文档
def upsert_document(db: Session, project_id: str, doc_type: str, content: str, title: str = None, is_auto: bool = False):
    doc = get_document(db, project_id, doc_type)

    if doc:
        doc.content = content
        doc.version += 1
        doc.is_auto_generated = is_auto
        if title:
            doc.title = title
    else:
        doc = Document(
            project_id=project_id,
            doc_type=doc_type,
            title=title or doc_type.upper(),
            content=content,
            is_auto_generated=is_auto
        )
        db.add(doc)

    db.commit()
    db.refresh(doc)
    return doc


# 更新文档
def update_document(db: Session, project_id: str, doc_type: str, data: DocumentUpdate):
    doc = get_document(db, project_id, doc_type)
    if not doc:
        return None

    doc.content = data.content
    doc.version += 1
    doc.change_reason = data.change_reason
    doc.is_auto_generated = False

    db.commit()
    db.refresh(doc)
    return doc


# 删除文档
def delete_document(db: Session, project_id: str, doc_type: str):
    doc = get_document(db, project_id, doc_type)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
