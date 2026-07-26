# 文档相关的API接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.document import DocumentResponse, DocumentUpdate, DocumentGenerateRequest
from app.services.document_service import (
    get_documents,
    get_document,
    update_document,
    delete_document,
    upsert_document
)

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["文档管理"])


@router.get("", response_model=list[DocumentResponse])
def list_documents(project_id: str, db: Session = Depends(get_db)):
    """获取项目文档列表"""
    return get_documents(db, project_id)


@router.get("/{doc_type}", response_model=DocumentResponse)
def get(project_id: str, doc_type: str, db: Session = Depends(get_db)):
    """获取指定类型的文档"""
    doc = get_document(db, project_id, doc_type)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


@router.put("/{doc_type}", response_model=DocumentResponse)
def update(project_id: str, doc_type: str, data: DocumentUpdate, db: Session = Depends(get_db)):
    """更新文档"""
    doc = update_document(db, project_id, doc_type, data)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


@router.delete("/{doc_type}")
def delete(project_id: str, doc_type: str, db: Session = Depends(get_db)):
    """删除文档"""
    success = delete_document(db, project_id, doc_type)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "删除成功"}


@router.post("/{doc_type}/generate", response_model=DocumentResponse)
def generate(project_id: str, doc_type: str, data: DocumentGenerateRequest, db: Session = Depends(get_db)):
    """
    AI生成文档
    - doc_type: readme, prd, star, resume, project_intro
    """
    # TODO: 接入LLM生成文档
    # 这里先返回一个示例内容
    sample_content = f"# {doc_type.upper()}\n\n这是AI生成的{doc_type}文档。\n\n> 指令: {data.instruction or '无'}"

    return upsert_document(db, project_id, doc_type, sample_content, is_auto=True)
