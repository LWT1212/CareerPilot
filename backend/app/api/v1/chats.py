# 聊天相关的API接口
# 支持：全局聊天（不隶属项目）+ 项目聊天

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse, MessageListResponse
from app.services.chat_service import (
    create_chat,
    get_chats,
    get_global_chats,
    get_chat,
    delete_chat,
    send_message,
    ai_reply,
    get_messages
)

# 全局聊天路由
router = APIRouter(prefix="/chats", tags=["全局聊天"])


# 创建全局聊天（不属于任何项目）
@router.post("", response_model=ChatResponse)
def create_global_chat(chat_data: ChatCreate, db: Session = Depends(get_db)):
    """创建全局聊天（不隶属于任何项目）"""
    return create_chat(db, None, chat_data)


# 获取全局聊天列表
@router.get("", response_model=list[ChatResponse])
def list_global_chats(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取全局聊天列表"""
    chats, _ = get_global_chats(db, skip, limit)
    return chats


# 项目聊天路由
project_router = APIRouter(prefix="/projects/{project_id}/chats", tags=["项目聊天"])


# 创建项目聊天
@project_router.post("", response_model=ChatResponse)
def create(project_id: str, chat_data: ChatCreate, db: Session = Depends(get_db)):
    """创建项目下的聊天"""
    return create_chat(db, project_id, chat_data)


# 获取项目聊天列表
@project_router.get("", response_model=list[ChatResponse])
def list_chats(project_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取项目下的聊天列表"""
    chats, _ = get_chats(db, project_id, skip, limit)
    return chats


# 获取单个聊天
@project_router.get("/{chat_id}", response_model=ChatResponse)
def get(project_id: str, chat_id: str, db: Session = Depends(get_db)):
    """获取聊天详情"""
    chat = get_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="聊天不存在")
    return chat


# 删除聊天
@project_router.delete("/{chat_id}")
def delete(project_id: str, chat_id: str, db: Session = Depends(get_db)):
    """删除聊天"""
    success = delete_chat(db, chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="聊天不存在")
    return {"message": "删除成功"}


# 消息路由
message_router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["消息"])


# 发送消息
@message_router.post("", response_model=MessageResponse)
def send(chat_id: str, message_data: MessageCreate, db: Session = Depends(get_db)):
    """
    发送消息并获取AI回复
    - content: 消息内容
    """
    # 保存用户消息
    send_message(db, chat_id, message_data)

    # 这里应该调用Agent处理，现在先返回简单回复
    # TODO: 接入Multi-Agent系统
    ai_content = f"收到你的消息：{message_data.content}"

    # 保存AI回复
    ai_message = ai_reply(db, chat_id, ai_content)

    return ai_message


# 获取消息列表
@message_router.get("", response_model=MessageListResponse)
def list_messages(chat_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """获取聊天消息列表"""
    messages, total = get_messages(db, chat_id, skip, limit)
    return MessageListResponse(items=messages, total=total)
