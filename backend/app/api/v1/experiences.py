# 经验相关的API接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from app.services.experience_service import (
    create_experience,
    get_experiences,
    get_experience,
    update_experience,
    delete_experience
)

router = APIRouter(prefix="/projects/{project_id}/experiences", tags=["经验管理"])


@router.post("", response_model=ExperienceResponse)
def create(project_id: str, data: ExperienceCreate, db: Session = Depends(get_db)):
    """创建开发经验"""
    return create_experience(db, project_id, data)


@router.get("", response_model=list[ExperienceResponse])
def list_experiences(project_id: str, type: str = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取经验列表"""
    exps, _ = get_experiences(db, project_id, type, skip, limit)
    return exps


@router.get("/{exp_id}", response_model=ExperienceResponse)
def get(project_id: str, exp_id: str, db: Session = Depends(get_db)):
    """获取经验详情"""
    exp = get_experience(db, exp_id, project_id)
    if not exp:
        raise HTTPException(status_code=404, detail="经验不存在")
    return exp


@router.put("/{exp_id}", response_model=ExperienceResponse)
def update(project_id: str, exp_id: str, data: ExperienceUpdate, db: Session = Depends(get_db)):
    """更新经验"""
    exp = update_experience(db, exp_id, data, project_id)
    if not exp:
        raise HTTPException(status_code=404, detail="经验不存在")
    return exp


@router.delete("/{exp_id}")
def delete(project_id: str, exp_id: str, db: Session = Depends(get_db)):
    """删除经验"""
    success = delete_experience(db, exp_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="经验不存在")
    return {"message": "删除成功"}
