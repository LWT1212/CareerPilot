# Agent工具集 - 让Agent能真实操作数据库
# 每个工具都是独立函数，LangGraph的Agent节点调用它们完成任务

from sqlalchemy.orm import Session
from app.models.experience import Experience
from app.models.interview import Interview, InterviewQuestion
from app.models.document import Document
from app.models.knowledge import KnowledgeDocument
from app.services.rag_service import search_documents


# ============ 经验工具 ============

def save_experience(db: Session, project_id: str, title: str, exp_type: str,
                    content: str, solution: str = None) -> dict:
    """
    保存开发经验到数据库
    返回: {"success": True, "id": "...", "message": "已保存"}
    """
    exp = Experience(
        project_id=project_id,
        title=title,
        type=exp_type,
        content=content,
        solution=solution,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return {"success": True, "id": exp.id, "message": f"经验「{title}」已保存"}


def get_recent_experiences(db: Session, project_id: str, limit: int = 5) -> list:
    """获取项目最近的开发经验"""
    exps = db.query(Experience).filter(
        Experience.project_id == project_id
    ).order_by(Experience.created_at.desc()).limit(limit).all()
    return [
        {"title": e.title, "type": e.type, "content": e.content[:100],
         "solution": e.solution}
        for e in exps
    ]


# ============ 面试工具 ============

def get_interview_stats(db: Session, project_id: str) -> dict:
    """获取项目面试统计（含薄弱点）"""
    total = db.query(Interview).filter(Interview.project_id == project_id).count()
    questions = db.query(InterviewQuestion).join(Interview).filter(
        Interview.project_id == project_id
    ).all()

    # 按类别统计
    from collections import Counter
    category_counter = Counter()
    weak_counter = Counter()
    for q in questions:
        if q.category:
            category_counter[q.category] += 1
            if q.rating is not None and q.rating <= 2:
                weak_counter[q.category] += 1

    weak_areas = [
        {"category": c, "weak_count": weak_counter[c], "total": category_counter[c]}
        for c in category_counter
        if weak_counter[c] > 0
    ]

    return {
        "total_interviews": total,
        "total_questions": len(questions),
        "by_category": [{"category": c, "count": n} for c, n in category_counter.items()],
        "weak_areas": weak_areas,
    }


# ============ 文档工具 ============

def save_document(db: Session, project_id: str, doc_type: str, content: str) -> dict:
    """保存文档（已有则更新版本）"""
    doc = db.query(Document).filter(
        Document.project_id == project_id,
        Document.doc_type == doc_type
    ).first()

    if doc:
        doc.content = content
        doc.version += 1
        doc.is_auto_generated = True
        message = f"文档 {doc_type} 已更新到 v{doc.version}"
    else:
        doc = Document(
            project_id=project_id,
            doc_type=doc_type,
            title=doc_type.upper(),
            content=content,
            is_auto_generated=True,
        )
        db.add(doc)
        message = f"文档 {doc_type} 已创建"
    db.commit()
    db.refresh(doc)
    return {"success": True, "id": doc.id, "message": message}


def get_document(db: Session, project_id: str, doc_type: str) -> dict:
    """获取项目指定文档"""
    doc = db.query(Document).filter(
        Document.project_id == project_id,
        Document.doc_type == doc_type
    ).first()
    if not doc:
        return {"exists": False, "message": f"还没有{doc_type}文档"}
    return {"exists": True, "title": doc.title, "content": doc.content[:500], "version": doc.version}


# ============ 知识库工具 ============

def search_project_knowledge(db: Session, project_id: str, query: str, top_k: int = 3) -> list:
    """语义检索项目知识库"""
    results = search_documents(project_id, query, top_k)
    return [
        {"content": r["content"][:200], "score": round(r["score"], 2)}
        for r in results
    ]


# 工具注册表（供Agent节点引用）
TOOLS = {
    "save_experience": save_experience,
    "get_recent_experiences": get_recent_experiences,
    "get_interview_stats": get_interview_stats,
    "save_document": save_document,
    "get_document": get_document,
    "search_project_knowledge": search_project_knowledge,
}

TOOL_DESCRIPTIONS = {
    "save_experience": "保存开发经验。参数: title(标题), exp_type(bug/solution/architecture/lesson/note), content(内容), solution(解决方案,可选)。当用户想记录经验时调用。",
    "get_recent_experiences": "获取项目最近的开发经验。参数: 无。当用户想查看已有经验时调用。",
    "get_interview_stats": "获取项目面试统计和薄弱点。参数: 无。当用户问面试情况/薄弱点时调用。",
    "save_document": "保存文档。参数: doc_type(readme/prd/star/resume), content(内容)。当用户要求生成文档时调用。",
    "get_document": "获取项目文档。参数: doc_type。当用户询问已有文档时调用。",
    "search_project_knowledge": "检索项目知识库。参数: query(查询词)。当用户询问技术知识时调用。",
}


# ============ MCP 外部工具（T17） ============
from app.services.mcp_client_service import (
    github_repo_info as mcp_github_repo_info,
    web_search as mcp_web_search,
    read_local_file as mcp_read_local_file,
)

# 注册到工具注册表（供Agent调用）
TOOLS["github_repo_info"] = mcp_github_repo_info
TOOLS["web_search"] = mcp_web_search
TOOLS["read_local_file"] = mcp_read_local_file

TOOL_DESCRIPTIONS["github_repo_info"] = "查询GitHub仓库信息。参数: repo(用户名/仓库名)。用户想了解某个开源项目/仓库时调用。"
TOOL_DESCRIPTIONS["web_search"] = "网页搜索。参数: query(搜索关键词)。用户想查找网上资料/最新信息时调用。"
TOOL_DESCRIPTIONS["read_local_file"] = "读取本地文件。参数: filepath(文件路径)。用户想查看项目代码文件时调用。"
