# 面试相关的数据模型

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# 创建面试请求
class InterviewCreate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    interview_date: Optional[date] = None
    interviewer: Optional[str] = None
    status: str = "completed"
    overall_feedback: Optional[str] = None
    result: Optional[str] = None
    notes: Optional[str] = None


# 面试响应
class InterviewResponse(BaseModel):
    id: str
    project_id: str
    company: Optional[str]
    position: Optional[str]
    interview_date: Optional[date]
    interviewer: Optional[str]
    status: str
    overall_feedback: Optional[str]
    result: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# 添加面试问题请求
class InterviewQuestionCreate(BaseModel):
    question: str
    user_answer: Optional[str] = None
    interviewer_feedback: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    rating: Optional[int] = None
    learning_suggestion: Optional[str] = None
    is_weak_point: int = 0


# 面试问题响应
class InterviewQuestionResponse(BaseModel):
    id: str
    interview_id: str
    question: str
    user_answer: Optional[str]
    interviewer_feedback: Optional[str]
    category: Optional[str]
    difficulty: Optional[str]
    rating: Optional[int]
    learning_suggestion: Optional[str]
    is_weak_point: int
    created_at: datetime

    class Config:
        from_attributes = True


# 面试统计响应
class InterviewStatsResponse(BaseModel):
    total_interviews: int
    total_questions: int
    by_company: List[dict]
    weak_areas: List[dict]
