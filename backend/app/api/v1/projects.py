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
