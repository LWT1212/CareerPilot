# 项目服务 - 处理项目相关的业务逻辑

from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


# 创建项目
def create_project(db: Session, project_data: ProjectCreate, owner_id: str):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        icon=project_data.icon,
        owner_id=owner_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# 获取项目列表
def get_projects(db: Session, owner_id: str, skip: int = 0, limit: int = 20):
    projects = db.query(Project).filter(
        Project.owner_id == owner_id,
        Project.status != "deleted"
    ).offset(skip).limit(limit).all()
    total = db.query(Project).filter(
        Project.owner_id == owner_id,
        Project.status != "deleted"
    ).count()
    return projects, total


# 获取单个项目
def get_project(db: Session, project_id: str, owner_id: str):
    return db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == owner_id
    ).first()


# 更新项目
def update_project(db: Session, project_id: str, project_data: ProjectUpdate, owner_id: str):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == owner_id
    ).first()

    if not project:
        return None

    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


# 删除项目（软删除）
def delete_project(db: Session, project_id: str, owner_id: str):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == owner_id
    ).first()

    if not project:
        return False

    project.status = "deleted"
    db.commit()
    return True
