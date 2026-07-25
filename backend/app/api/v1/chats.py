# 聊天相关的API接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse, MessageListResponse
from app.services.chat_service import (
    create_chat,
    get_chats,
    get_chat,
    delete_chat,
    send_message,
    ai_reply,
    get_messages
)

# 创建路由
router = APIRouter(prefix="/projects/{project_id}/chats", tags=["聊天系统"])


# 创建聊天
@router.post("", response_model=ChatResponse)
def create(project_id: str, chat_data: ChatCreate, db: Session = Depends(get_db)):
    """创建新的聊天会话"""
    return create_chat(db, project_id, chat_data)


# 获取聊天列表
@router.get("", response_model=list[ChatResponse])
def list_chats(project_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取项目下的聊天列表"""
    chats, _ = get_chats(db, project_id, skip, limit)
    return chats


# 获取单个聊天
@router.get("/{chat_id}", response_model=ChatResponse)
def get(project_id: str, chat_id: str, db: Session = Depends(get_db)):
    """获取聊天详情"""
    chat = get_chat(db, chat_id, project_id)
    if not chat:
        raise HTTPException(status_code=404, detail="聊天不存在")
    return chat


# 删除聊天
@router.delete("/{chat_id}")
def delete(project_id: str, chat_id: str, db: Session = Depends(get_db)):
    """删除聊天"""
    success = delete_chat(db, chat_id, project_id)
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
    user_message = send_message(db, chat_id, message_data)

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
