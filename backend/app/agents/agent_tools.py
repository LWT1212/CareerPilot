# Agent工具集 - 让Agent能真实操作数据库
# 每个工具调用对应 service 层（不直接写DB操作），保持分层清晰

from app.services.experience_service import (
    create_experience as svc_create_experience,
    get_experiences as svc_get_experiences,
)
from app.services.interview_service import get_stats as svc_get_interview_stats
from app.services.document_service import (
    upsert_document as svc_upsert_document,
    get_document as svc_get_document,
)
from app.services.knowledge_service import search_knowledge as svc_search_knowledge


# ============ 经验工具 ============

def save_experience(db, project_id: str, title: str, exp_type: str,
                    content: str, solution: str = None) -> dict:
    """
    保存开发经验到数据库（调用 experience_service）
    返回: {"success": True, "id": "...", "message": "已保存"}
    """
    from app.schemas.experience import ExperienceCreate

    data = ExperienceCreate(
        title=title,
        type=exp_type,
        content=content,
        solution=solution,
        tags=[],
    )
    exp = svc_create_experience(db, project_id, data)
    return {"success": True, "id": exp.id, "message": f"经验「{title}」已保存"}


def get_recent_experiences(db, project_id: str, limit: int = 5) -> list:
    """获取项目最近的开发经验（调用 experience_service）"""
    exps, _ = svc_get_experiences(db, project_id, limit=limit)
    return [
        {"title": e.title, "type": e.type, "content": e.content[:100],
         "solution": e.solution}
        for e in exps
    ]


# ============ 面试工具 ============

def get_interview_stats(db, project_id: str) -> dict:
    """获取项目面试统计（调用 interview_service）"""
    return svc_get_interview_stats(db, project_id)


# ============ 文档工具 ============

def save_document(db, project_id: str, doc_type: str, content: str) -> dict:
    """保存文档（调用 document_service，已有则更新版本）"""
    doc = svc_upsert_document(db, project_id, doc_type, content, is_auto=True)
    return {"success": True, "id": doc.id, "message": f"文档 {doc_type} 已保存 v{doc.version}"}


def get_document(db, project_id: str, doc_type: str) -> dict:
    """获取项目指定文档（调用 document_service）"""
    doc = svc_get_document(db, project_id, doc_type)
    if not doc:
        return {"exists": False, "message": f"还没有{doc_type}文档"}
    return {"exists": True, "title": doc.title, "content": doc.content[:500], "version": doc.version}


# ============ 知识库工具 ============

async def search_project_knowledge(db, project_id: str, query: str, top_k: int = 3) -> list:
    """语义检索项目知识库（调用 knowledge_service，async）"""
    results = await svc_search_knowledge(db, project_id, query, top_k)
    return [
        {"content": r.content[:200], "score": round(r.score, 2)}
        for r in results
    ]


# ============ MCP 外部工具（T17） ============
from app.services.mcp_client_service import (
    github_repo_info as mcp_github_repo_info,
    web_search as mcp_web_search,
    read_local_file as mcp_read_local_file,
)

# 注册到工具注册表（供Agent调用）
TOOLS = {
    "save_experience": save_experience,
    "get_recent_experiences": get_recent_experiences,
    "get_interview_stats": get_interview_stats,
    "save_document": save_document,
    "get_document": get_document,
    "search_project_knowledge": search_project_knowledge,
    "github_repo_info": mcp_github_repo_info,
    "web_search": mcp_web_search,
    "read_local_file": mcp_read_local_file,
}

TOOL_DESCRIPTIONS = {
    "save_experience": "保存开发经验。参数: title(标题), exp_type(bug/solution/architecture/lesson/note), content(内容), solution(解决方案,可选)。当用户想记录经验时调用。",
    "get_recent_experiences": "获取项目最近的开发经验。参数: 无。当用户想查看已有经验时调用。",
    "get_interview_stats": "获取项目面试统计和薄弱点。参数: 无。当用户问面试情况/薄弱点时调用。",
    "save_document": "保存文档。参数: doc_type(readme/prd/star/resume), content(内容)。当用户要求生成文档时调用。",
    "get_document": "获取项目文档。参数: doc_type。当用户询问已有文档时调用。",
    "search_project_knowledge": "检索项目知识库。参数: query(查询词)。当用户询问技术知识时调用。",
    "github_repo_info": "查询GitHub仓库信息。参数: repo(用户名/仓库名)。用户想了解某个开源项目/仓库时调用。",
    "web_search": "网页搜索。参数: query(搜索关键词)。用户想查找网上资料/最新信息时调用。",
    "read_local_file": "读取本地文件。参数: filepath(文件路径)。用户想查看项目代码文件时调用。",
}
