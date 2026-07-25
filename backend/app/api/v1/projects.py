# 项目相关的API接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
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
def create(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """
    创建新项目
    - name: 项目名称（必填）
    - description: 项目描述（可选）
    - icon: 项目图标（可选）
    """
    # 这里暂时用固定用户ID，后面会改成从Token获取
    owner_id = "current_user_id"
    return create_project(db, project_data, owner_id)


# 获取项目列表
# GET /api/v1/projects
@router.get("", response_model=ProjectListResponse)
def list_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取当前用户的项目列表"""
    owner_id = "current_user_id"
    projects, total = get_projects(db, owner_id, skip, limit)
    return ProjectListResponse(items=projects, total=total)


# 获取单个项目
# GET /api/v1/projects/{project_id}
@router.get("/{project_id}", response_model=ProjectResponse)
def get(project_id: str, db: Session = Depends(get_db)):
    """获取项目详情"""
    owner_id = "current_user_id"
    project = get_project(db, project_id, owner_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


# 更新项目
# PUT /api/v1/projects/{project_id}
@router.put("/{project_id}", response_model=ProjectResponse)
def update(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db)):
    """更新项目信息"""
    owner_id = "current_user_id"
    project = update_project(db, project_id, project_data, owner_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


# 删除项目
# DELETE /api/v1/projects/{project_id}
@router.delete("/{project_id}")
def delete(project_id: str, db: Session = Depends(get_db)):
    """删除项目（软删除）"""
    owner_id = "current_user_id"
    success = delete_project(db, project_id, owner_id)
    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"message": "删除成功"}
