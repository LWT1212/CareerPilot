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
    发送消息并获取AI回复（多智能体调度）
    - content: 消息内容
    """
    # 1. 保存用户消息
    send_message(db, chat_id, message_data)

    # 2. 获取历史消息（供LLM理解上下文）
    history = messages_to_llm_history(db, chat_id)

    # 3. 获取聊天所属项目（用于RAG）
    chat = get_chat(db, chat_id)
    project_id = chat.project_id if chat else None

    # 4. 检查Skill触发（如"沉淀这个经验"）
    from app.skills.skills_manager import skills_manager
    skill = skills_manager.match(message_data.content)

    if skill:
        # 命中Skill → 执行Skill作为回复
        try:
            ai_content = await skills_manager.execute(skill.name, {
                "message": message_data.content,
                "project_id": project_id or "",
                "db": db,
                "chat_history": history,
            })
            agent_used = f"skill:{skill.name}"
        except Exception as e:
            print(f"Skill执行失败: {e}")
            ai_content = "（技能执行失败，请重试）"
            agent_used = "skill_error"
    else:
        # 未命中Skill → 走LangGraph多智能体
        try:
            from app.agents.langgraph_workflow import run_agent
            result = await run_agent(message_data.content, project_id or "", history, db)
            ai_content = result.get("response", "")
            agent_used = result.get("intent", "llm")
            if not ai_content:
                ai_content = "（未能生成回复）"
        except Exception as e:
            # LLM调用失败时返回友好提示
            print(f"多智能体调用失败: {e}")
            ai_content = "（AI服务暂时不可用，请检查LLM配置：OPENAI_API_KEY 或 Ollama服务）"
            agent_used = "error"

    # 5. 保存AI回复
    ai_message = ai_reply(db, chat_id, ai_content, agent_used)

    # 6. 沉淀记忆（每5条消息触发一次，LLM提取决策/进度/问题/偏好）
    if project_id:
        try:
            from app.models.chat import Message as MsgModel
            from app.services.memory_service import extract_memories_from_messages
            count = db.query(MsgModel).filter(MsgModel.chat_id == chat_id).count()
            if count % 5 == 0 and count >= 5:
                await extract_memories_from_messages(db, chat_id, project_id)
                # 主动成长：沉淀后检查文档是否需要更新
                try:
                    from app.services.proactive_service import check_document_updates
                    await check_document_updates(db, project_id)
                except Exception as e:
                    print(f"文档更新检查失败: {e}")
                # 自动沉淀经验Skill：把问题+答案存入experiences
                try:
                    from app.skills.skills_manager import skills_manager
                    await skills_manager.execute("experience_curator", {
                        "message": message_data.content,
                        "project_id": project_id,
                        "db": db,
                        "chat_history": history,
                    })
                except Exception as e:
                    print(f"经验沉淀失败: {e}")
        except Exception as e:
            print(f"记忆沉淀失败: {e}")

    return ai_message


# 获取消息列表
@message_router.get("", response_model=MessageListResponse)
def list_messages(chat_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """获取聊天消息列表"""
    messages, total = get_messages(db, chat_id, skip, limit)
    return MessageListResponse(items=messages, total=total)


# 流式发送消息（SSE）- 走多智能体调度
@message_router.post("/stream")
async def stream_send(chat_id: str, message_data: MessageCreate, db: Session = Depends(get_db)):
    """
    流式发送消息（SSE）
    1. 多智能体意图识别（发送agent事件）
    2. 必要时执行Agent工具
    3. 最终回复流式输出
    """
    from fastapi.responses import StreamingResponse
    from app.agents.langgraph_workflow import coordinator_node
    from app.services.llm_service import chat_completion, stream_completion
    from app.agents.agent_tools import TOOL_DESCRIPTIONS, TOOLS

    # 1. 保存用户消息
    send_message(db, chat_id, message_data)

    # 2. 获取历史消息 + 项目
    history = messages_to_llm_history(db, chat_id)
    chat = get_chat(db, chat_id)
    project_id = chat.project_id if chat else None

    async def event_generator():
        full_content = ""
        try:
            # 3. 意图识别（复用LangGraph的coordinator节点逻辑）
            intent = "chat"
            try:
                intent_raw = await chat_completion(
                    [], message_data.content,
                    "你是任务调度器。判断用户消息的意图，只返回以下之一：knowledge/experience/interview/document/chat。只返回单词。"
                )
                for valid in ["knowledge", "experience", "interview", "document", "chat"]:
                    if valid in intent_raw.lower():
                        intent = valid
                        break
            except Exception:
                intent = "chat"

            # 发送Agent调度事件
            yield f"data: {json.dumps({'type': 'agent', 'name': 'coordinator', 'status': 'recognized', 'intent': intent})}\n\n"

            # 4. 简单工具执行（经验/文档保存类）
            if intent in ("experience", "document") and project_id:
                tool_desc = "\n".join(f"- {name}: {TOOL_DESCRIPTIONS[name]}" for name in TOOL_DESCRIPTIONS)
                try:
                    decision = await chat_completion(
                        [], message_data.content,
                        f"判断是否调用工具（{tool_desc}）。调用则输出 TOOL:工具名(参数=值)；否则 NONE。只输出一行。"
                    )
                    if decision.strip().startswith("TOOL:"):
                        tool_line = decision.strip()[5:]
                        tool_name = tool_line.split("(")[0].strip()
                        args = {}
                        if "(" in tool_line:
                            for pair in tool_line.split("(", 1)[1].rstrip(")").split(","):
                                if "=" in pair:
                                    k, v = pair.split("=", 1)
                                    args[k.strip()] = v.strip().strip("'\"")
                        if tool_name in TOOLS and db is not None:
                            args["db"] = db
                            args["project_id"] = project_id
                            tool_result = TOOLS[tool_name](**args)
                            yield f"data: {json.dumps({'type': 'agent', 'name': intent, 'status': 'tool', 'tool': tool_name, 'message': tool_result.get('message', '')})}\n\n"
                except Exception as e:
                    print(f"工具执行失败: {e}")

            # 5. 流式生成最终回复
            system_prompt = ""
            if intent == "knowledge" and project_id:
                from app.services.rag_service import build_rag_context
                context = build_rag_context(project_id, message_data.content, top_k=3)
                if context:
                    system_prompt = f"你是知识助手，请基于资料回答：\n【资料】\n{context}"
            elif intent == "experience":
                system_prompt = "你是经验助手，帮助开发者整理开发经验和解决方案。"
            elif intent == "interview":
                system_prompt = "你是面试助手，分析面试表现、识别薄弱点、给出学习建议。"
            elif intent == "document":
                system_prompt = "你是文档助手，生成结构清晰专业的文档。"
            else:
                system_prompt = "你是CareerPilot AI助手，帮助开发者进行技术讨论。"

            async for chunk in stream_completion(history, message_data.content, system_prompt):
                full_content += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            print(f"多智能体流式调用失败: {e}")
            error_msg = "（AI服务暂时不可用，请检查LLM配置）"
            full_content = error_msg
            yield f"data: {json.dumps({'type': 'chunk', 'content': error_msg})}\n\n"

        # 保存完整的AI回复
        ai_reply(db, chat_id, full_content, intent)
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
