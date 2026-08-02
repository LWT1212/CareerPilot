# 聊天相关的API接口
# 支持：全局聊天（不隶属项目）+ 项目聊天

import json
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
    get_messages,
    messages_to_llm_history
)
from app.services.llm_service import chat_completion, stream_completion
from app.services.rag_service import build_rag_context


def _build_system_prompt(db: Session, chat_id: str, user_message: str) -> str:
    """
    构建系统提示词
    如果聊天属于某个项目，检索该项目知识库作为RAG上下文
    """
    # 获取聊天的项目
    chat = get_chat(db, chat_id)
    if not chat or not chat.project_id:
        return ""  # 全局聊天无RAG

    # 检索项目知识库
    context = build_rag_context(chat.project_id, user_message, top_k=3)
    if not context:
        return ""

    return (
        "你是CareerPilot AI助手，请基于以下项目知识库内容回答用户问题。\n"
        "如果知识库中没有相关信息，请如实说明。\n\n"
        "【项目知识库】\n"
        f"{context}"
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
async def send(chat_id: str, message_data: MessageCreate, db: Session = Depends(get_db)):
    """
    发送消息并获取AI回复
    - content: 消息内容
    """
    # 1. 保存用户消息
    send_message(db, chat_id, message_data)

    # 2. 获取历史消息（供LLM理解上下文）
    history = messages_to_llm_history(db, chat_id)

    # 3. 构建RAG上下文（项目聊天自动检索知识库）
    system_prompt = _build_system_prompt(db, chat_id, message_data.content)

    # 4. 调用真实LLM生成回复
    try:
        ai_content = await chat_completion(history, message_data.content, system_prompt)
        agent_used = "llm"
    except Exception as e:
        # LLM调用失败时返回友好提示
        print(f"LLM调用失败: {e}")
        ai_content = "（AI服务暂时不可用，请检查LLM配置：OPENAI_API_KEY 或 Ollama服务）"
        agent_used = "error"

    # 5. 保存AI回复
    ai_message = ai_reply(db, chat_id, ai_content, agent_used)

    return ai_message


# 获取消息列表
@message_router.get("", response_model=MessageListResponse)
def list_messages(chat_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """获取聊天消息列表"""
    messages, total = get_messages(db, chat_id, skip, limit)
    return MessageListResponse(items=messages, total=total)


# 流式发送消息（SSE）
@message_router.post("/stream")
async def stream_send(chat_id: str, message_data: MessageCreate, db: Session = Depends(get_db)):
    """
    流式发送消息（SSE）
    前端实时显示AI逐字回复
    """
    from fastapi.responses import StreamingResponse

    # 1. 保存用户消息
    send_message(db, chat_id, message_data)

    # 2. 获取历史消息
    history = messages_to_llm_history(db, chat_id)

    # 3. 构建RAG上下文（项目聊天自动检索知识库）
    system_prompt = _build_system_prompt(db, chat_id, message_data.content)

    async def event_generator():
        full_content = ""
        try:
            # 流式获取LLM回复
            async for chunk in stream_completion(history, message_data.content, system_prompt):
                full_content += chunk
                # SSE格式：data: {...}\n\n
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            print(f"LLM流式调用失败: {e}")
            error_msg = "（AI服务暂时不可用，请检查LLM配置）"
            full_content = error_msg
            yield f"data: {json.dumps({'type': 'chunk', 'content': error_msg})}\n\n"

        # 3. 保存完整的AI回复
        ai_reply(db, chat_id, full_content, "llm")
        # 发送完成事件
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
