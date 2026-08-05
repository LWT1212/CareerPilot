# 项目相关的API接口（需认证）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.services.project_service import (
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project
)

# 创建路由
router = APIRouter(prefix="/projects", tags=["项目管理"])


# 创建项目
# POST /api/v1/projects
@router.post("", response_model=ProjectResponse)
def create(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新项目
    - name: 项目名称（必填）
    - description: 项目描述（可选）
    - icon: 项目图标（可选）
    """
    return create_project(db, project_data, current_user.id)


# 获取项目列表
# GET /api/v1/projects
@router.get("", response_model=ProjectListResponse)
def list_projects(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的项目列表"""
    projects, total = get_projects(db, current_user.id, skip, limit)
    return ProjectListResponse(items=projects, total=total)


# 获取单个项目
# GET /api/v1/projects/{project_id}
@router.get("/{project_id}", response_model=ProjectResponse)
def get(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目详情"""
    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


# 更新项目
# PUT /api/v1/projects/{project_id}
@router.put("/{project_id}", response_model=ProjectResponse)
def update(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新项目信息"""
    project = update_project(db, project_id, project_data, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


# 删除项目
# DELETE /api/v1/projects/{project_id}
@router.delete("/{project_id}")
def delete(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除项目（软删除）"""
    success = delete_project(db, project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"message": "删除成功"}


# 获取项目记忆
@router.get("/{project_id}/memories")
def get_memories(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目长期记忆"""
    from app.services.memory_service import get_project_memories, get_recent_summaries

    # 校验项目归属
    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    memories = get_project_memories(db, project_id, importance_min=1, limit=50)
    summaries = get_recent_summaries(db, project_id=project_id, limit=10)

    return {
        "memories": [
            {
                "id": m.id,
                "memory_type": m.memory_type,
                "content": m.content,
                "importance": m.importance,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ],
        "summaries": [s.summary for s in summaries],
    }


# ============ 主动成长API ============

# 获取学习计划
@router.get("/{project_id}/learning-plans")
def get_plans(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取AI生成的学习计划（面试薄弱点）"""
    from app.services.proactive_service import get_learning_plans

    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    plans = get_learning_plans(db, project_id)
    return [
        {
            "id": p.id,
            "category": p.category,
            "title": p.title,
            "content": p.content,
            "weak_count": p.weak_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in plans
    ]


# 获取提醒
@router.get("/{project_id}/notifications")
def get_notifs(
    project_id: str,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取AI主动提醒"""
    from app.services.proactive_service import get_notifications

    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    notifs = get_notifications(db, project_id, unread_only)
    return [
        {
            "id": n.id,
            "ntype": n.ntype,
            "title": n.title,
            "content": n.content,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


# 标记提醒已读
@router.post("/{project_id}/notifications/{notif_id}/read")
def mark_read(
    project_id: str,
    notif_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记提醒已读"""
    from app.services.proactive_service import mark_notification_read

    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    success = mark_notification_read(db, notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="提醒不存在")
    return {"message": "已标记为已读"}
