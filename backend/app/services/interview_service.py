# 面试服务

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.interview import Interview, InterviewQuestion
from app.schemas.interview import InterviewCreate, InterviewQuestionCreate


# 创建面试
def create_interview(db: Session, project_id: str, data: InterviewCreate):
    interview = Interview(project_id=project_id, **data.model_dump())
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


# 获取面试列表
def get_interviews(db: Session, project_id: str, skip: int = 0, limit: int = 20):
    interviews = db.query(Interview).filter(
        Interview.project_id == project_id
    ).order_by(Interview.interview_date.desc()).offset(skip).limit(limit).all()
    total = db.query(Interview).filter(Interview.project_id == project_id).count()
    return interviews, total


# 获取单个面试
def get_interview(db: Session, interview_id: str, project_id: str):
    return db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.project_id == project_id
    ).first()


# 删除面试
def delete_interview(db: Session, interview_id: str, project_id: str):
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.project_id == project_id
    ).first()
    if not interview:
        return False
    db.delete(interview)
    db.commit()
    return True


# 添加面试问题
def add_question(db: Session, interview_id: str, data: InterviewQuestionCreate):
    question = InterviewQuestion(interview_id=interview_id, **data.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


# 获取面试统计
def get_stats(db: Session, project_id: str):
    # 总面试数
    total_interviews = db.query(Interview).filter(
        Interview.project_id == project_id
    ).count()

    # 总问题数
    total_questions = db.query(InterviewQuestion).join(Interview).filter(
        Interview.project_id == project_id
    ).count()

    # 按公司统计
    by_company = db.query(
        Interview.company,
        func.count(Interview.id)
    ).filter(
        Interview.project_id == project_id
    ).group_by(Interview.company).all()

    # 薄弱点统计（rating <= 2 的问题分类）
    weak_areas = db.query(
        InterviewQuestion.category,
        func.count(InterviewQuestion.id)
    ).join(Interview).filter(
        Interview.project_id == project_id,
        InterviewQuestion.rating <= 2,
        InterviewQuestion.category.isnot(None)
    ).group_by(InterviewQuestion.category).all()

    return {
        "total_interviews": total_interviews,
        "total_questions": total_questions,
        "by_company": [{"company": c, "count": n} for c, n in by_company],
        "weak_areas": [{"category": c, "count": n} for c, n in weak_areas]
    }
