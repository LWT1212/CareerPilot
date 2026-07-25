# 经验服务

from sqlalchemy.orm import Session
from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate, ExperienceUpdate


# 创建经验
def create_experience(db: Session, project_id: str, data: ExperienceCreate):
    exp = Experience(
        project_id=project_id,
        title=data.title,
        type=data.type,
        content=data.content,
        solution=data.solution,
        tags=data.tags
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


# 获取经验列表
def get_experiences(db: Session, project_id: str, type_filter: str = None, skip: int = 0, limit: int = 20):
    query = db.query(Experience).filter(Experience.project_id == project_id)
    if type_filter:
        query = query.filter(Experience.type == type_filter)
    exps = query.order_by(Experience.is_pinned.desc(), Experience.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()
    return exps, total


# 获取单个经验
def get_experience(db: Session, exp_id: str, project_id: str):
    return db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.project_id == project_id
    ).first()


# 更新经验
def update_experience(db: Session, exp_id: str, data: ExperienceUpdate, project_id: str):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.project_id == project_id
    ).first()
    if not exp:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(exp, key, value)
    db.commit()
    db.refresh(exp)
    return exp


# 删除经验
def delete_experience(db: Session, exp_id: str, project_id: str):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.project_id == project_id
    ).first()
    if not exp:
        return False
    db.delete(exp)
    db.commit()
    return True
