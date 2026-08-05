# 面试相关的API接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewQuestionCreate,
    InterviewQuestionResponse,
    InterviewStatsResponse
)
from app.services.interview_service import (
    create_interview,
    get_interviews,
    get_interview,
    delete_interview,
    add_question,
    get_stats
)

router = APIRouter(prefix="/projects/{project_id}/interviews", tags=["面试管理"])


@router.post("", response_model=InterviewResponse)
def create(project_id: str, data: InterviewCreate, db: Session = Depends(get_db)):
    """创建面试记录"""
    return create_interview(db, project_id, data)


@router.get("", response_model=list[InterviewResponse])
def list_interviews(project_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取面试列表"""
    interviews, _ = get_interviews(db, project_id, skip, limit)
    return interviews


@router.get("/stats", response_model=InterviewStatsResponse)
def stats(project_id: str, db: Session = Depends(get_db)):
    """获取面试统计"""
    return get_stats(db, project_id)


@router.get("/{interview_id}", response_model=InterviewResponse)
def get(project_id: str, interview_id: str, db: Session = Depends(get_db)):
    """获取面试详情"""
    interview = get_interview(db, interview_id, project_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    return interview


@router.delete("/{interview_id}")
def delete(project_id: str, interview_id: str, db: Session = Depends(get_db)):
    """删除面试记录"""
    success = delete_interview(db, interview_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    return {"message": "删除成功"}


# 面试问题路由
question_router = APIRouter(prefix="/interviews/{interview_id}/questions", tags=["面试问题"])


@question_router.post("", response_model=InterviewQuestionResponse)
async def create_question(interview_id: str, data: InterviewQuestionCreate, db: Session = Depends(get_db)):
    """添加面试问题（自动检查薄弱点）"""
    question = add_question(db, interview_id, data)

    # 主动成长：检查薄弱点并生成学习计划（后台触发，不阻塞响应）
    try:
        from app.models.interview import Interview
        from app.services.proactive_service import analyze_interview_weakness
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if interview:
            await analyze_interview_weakness(db, interview.project_id)
    except Exception as e:
        print(f"薄弱点分析失败: {e}")

    return question
