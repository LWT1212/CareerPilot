# 知识库相关的API接口

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.knowledge import (
    KnowledgeDocumentResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse
)
from app.services.knowledge_service import (
    upload_document,
    get_documents,
    get_document,
    delete_document,
    search_knowledge
)

# 创建路由（项目知识库 + 全局知识库）
router = APIRouter(prefix="/projects/{project_id}/knowledge", tags=["知识库"])
global_router = APIRouter(prefix="/knowledge", tags=["全局知识库"])


# ============ 全局知识库 ============

# 上传到全局知识库
@global_router.post("", response_model=KnowledgeDocumentResponse)
async def upload_global(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传到全局知识库（不属于任何项目）"""
    file_content = file.file.read()
    file_type = file.filename.split(".")[-1].lower()
    if file_type not in ["pdf", "docx", "doc", "md", "txt"]:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    return upload_document(db, None, file.filename, file_content, file_type)


# 获取全局知识库列表
@global_router.get("", response_model=list[KnowledgeDocumentResponse])
def list_global_documents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取全局知识库文档列表"""
    docs, _ = get_documents(db, None, skip, limit)
    return docs


# ============ 项目知识库 ============

# 上传文档到项目
@router.post("", response_model=KnowledgeDocumentResponse)
async def upload(project_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    上传知识文档到项目
    支持格式：PDF, Word, Markdown, TXT
    """
    # 读取文件内容
    file_content = file.file.read()

    # 获取文件类型
    file_type = file.filename.split(".")[-1].lower()
    if file_type not in ["pdf", "docx", "doc", "md", "txt"]:
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    doc = upload_document(db, project_id, file.filename, file_content, file_type)

    # 主动成长：新文档影响分析（后台触发）
    if doc.embedding_status == "completed":
        try:
            from app.services.proactive_service import analyze_knowledge_impact
            content = doc.content or ""
            if content:
                await analyze_knowledge_impact(db, project_id, content)
        except Exception as e:
            print(f"知识库影响分析失败: {e}")

    return doc


# 获取文档列表
@router.get("", response_model=list[KnowledgeDocumentResponse])
def list_documents(project_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取知识库文档列表"""
    docs, _ = get_documents(db, project_id, skip, limit)
    return docs


# 获取单个文档
@router.get("/{doc_id}", response_model=KnowledgeDocumentResponse)
def get(project_id: str, doc_id: str, db: Session = Depends(get_db)):
    """获取文档详情"""
    doc = get_document(db, doc_id, project_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


# 删除文档
@router.delete("/{doc_id}")
def delete(project_id: str, doc_id: str, db: Session = Depends(get_db)):
    """删除知识文档"""
    success = delete_document(db, doc_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "删除成功"}


# 知识检索
@router.post("/search", response_model=KnowledgeSearchResponse)
def search(project_id: str, search_data: KnowledgeSearchRequest, db: Session = Depends(get_db)):
    """
    知识检索（RAG）
    - query: 搜索关键词
    - top_k: 返回结果数量
    """
    results = search_knowledge(db, project_id, search_data.query, search_data.top_k)
    return KnowledgeSearchResponse(
        results=results,
        query=search_data.query,
        total_results=len(results)
    )
