# Agent相关的API接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.agents import (
    CoordinatorAgent,
    KnowledgeAgent,
    ExperienceAgent,
    InterviewAgent,
    DocumentAgent
)

router = APIRouter(prefix="/agents", tags=["Agent系统"])

# 初始化Agent
coordinator = CoordinatorAgent()
knowledge = KnowledgeAgent()
experience = ExperienceAgent()
interview = InterviewAgent()
document = DocumentAgent()


@router.get("/status")
async def get_status():
    """获取Agent状态"""
    return {
        "agents": [
            {
                "type": "coordinator",
                "name": "Coordinator Agent",
                "status": "ready",
                "description": "统一调度，理解用户意图"
            },
            {
                "type": "knowledge",
                "name": "Knowledge Agent",
                "status": "ready",
                "description": "RAG检索，技术问答"
            },
            {
                "type": "experience",
                "name": "Experience Agent",
                "status": "ready",
                "description": "开发经验整理"
            },
            {
                "type": "interview",
                "name": "Interview Agent",
                "status": "ready",
                "description": "面试分析，成长建议"
            },
            {
                "type": "document",
                "name": "Document Agent",
                "status": "ready",
                "description": "文档自动生成"
            }
        ]
    }


@router.post("/chat")
async def chat(input_data: dict, db: Session = Depends(get_db)):
    """
    与Agent对话
    - content: 用户消息
    - project_id: 项目ID（可选）
    """
    # 1. Coordinator分析意图
    result = await coordinator.execute(input_data)
    agent_type = result.get("agent", "chat")

    # 2. 调用对应Agent
    if agent_type == "knowledge":
        response = await knowledge.execute(input_data)
    elif agent_type == "experience":
        response = await experience.execute(input_data)
    elif agent_type == "interview":
        response = await interview.execute(input_data)
    elif agent_type == "document":
        response = await document.execute(input_data)
    else:
        response = {
            "agent": "chat",
            "response": f"收到你的消息：{input_data.get('content', '')}"
        }

    return {
        "intent": result,
        "response": response
    }
