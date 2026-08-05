# 记忆服务 - 项目记忆的写入/读取/沉淀

from sqlalchemy.orm import Session
from app.models.project_memory import ProjectMemory
from app.models.chat_summary import ChatSummary
from app.models.chat import Message


# ============ 写入 ============

def add_memory(db: Session, project_id: str, memory_type: str,
               content: str, importance: int = 3, source_chat_id: str = None) -> ProjectMemory:
    """
    添加一条项目记忆（自动去重）
    去重规则：同项目 + 同类型 + 内容相似（前50字符相同）不重复写
    """
    # 去重检查
    existing = db.query(ProjectMemory).filter(
        ProjectMemory.project_id == project_id,
        ProjectMemory.memory_type == memory_type,
    ).all()
    for mem in existing:
        if mem.content[:50] == content[:50]:
            return mem  # 已存在，跳过

    memory = ProjectMemory(
        project_id=project_id,
        memory_type=memory_type,
        content=content,
        importance=importance,
        source_chat_id=source_chat_id,
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def add_chat_summary(db: Session, chat_id: str, summary: str) -> ChatSummary:
    """保存对话摘要"""
    record = ChatSummary(chat_id=chat_id, summary=summary)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ============ 读取 ============

def get_project_memories(db: Session, project_id: str, importance_min: int = 1, limit: int = 10) -> list:
    """获取项目记忆（按重要度降序）"""
    memories = db.query(ProjectMemory).filter(
        ProjectMemory.project_id == project_id,
        ProjectMemory.importance >= importance_min,
    ).order_by(ProjectMemory.importance.desc(), ProjectMemory.created_at.desc()).limit(limit).all()
    return memories


def get_recent_summaries(db: Session, chat_id: str = None, project_id: str = None, limit: int = 3) -> list:
    """
    获取最近对话摘要
    - 指定chat_id: 该聊天的摘要
    - 指定project_id: 该项目下所有聊天的摘要
    """
    query = db.query(ChatSummary)
    if chat_id:
        query = query.filter(ChatSummary.chat_id == chat_id)
    elif project_id:
        # 通过chats关联项目
        from app.models.chat import Chat
        chat_ids = [c.id for c in db.query(Chat).filter(Chat.project_id == project_id).all()]
        if not chat_ids:
            return []
        query = query.filter(ChatSummary.chat_id.in_(chat_ids))
    return query.order_by(ChatSummary.created_at.desc()).limit(limit).all()


def build_memory_prompt(db: Session, project_id: str) -> str:
    """
    构建记忆注入提示词
    组装项目记忆 + 最近摘要 → 供LLM注入system prompt
    """
    parts = []

    # 1. 项目记忆（重要度>=3，最多8条）
    memories = get_project_memories(db, project_id, importance_min=3, limit=8)
    if memories:
        mem_lines = []
        type_labels = {
            "decision": "决策", "progress": "进度",
            "problem": "问题", "preference": "偏好",
        }
        for m in memories:
            label = type_labels.get(m.memory_type, m.memory_type)
            mem_lines.append(f"- [{label}](重要度{m.importance}) {m.content}")
        parts.append("【项目记忆】\n" + "\n".join(mem_lines))

    # 2. 最近对话摘要
    summaries = get_recent_summaries(db, project_id=project_id, limit=3)
    if summaries:
        parts.append("【之前对话回顾】\n" + "\n\n".join(s.summary for s in summaries))

    return "\n\n".join(parts)


# ============ 沉淀 ============

async def extract_memories_from_messages(db: Session, chat_id: str, project_id: str):
    """
    从对话中提取记忆并沉淀（LLM提取）
    提取规则：决策/进度/问题/偏好 类信息
    """
    from app.services.llm_service import structured_completion
    from app.agents.agent_schemas import MemoriesExtractOutput

    # 获取该聊天的最近消息
    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).limit(20).all()
    if len(messages) < 4:
        return []  # 消息太少不沉淀

    # 组装对话文本（倒序恢复）
    conv_lines = []
    for msg in reversed(messages):
        role = "用户" if msg.role == "user" else "AI"
        conv_lines.append(f"{role}: {msg.content[:300]}")
    conv_text = "\n".join(conv_lines)

    try:
        result = await structured_completion(
            MemoriesExtractOutput,
            conv_text,
            "从对话中提取值得长期记忆的信息：决策(技术选型/方向选择)、进度(项目进展)、"
            "问题(遇到的重要问题)、偏好(用户的技术偏好)。没有可提取的返回空列表。"
        )
        added = []
        for item in result.memories:
            mem = add_memory(
                db, project_id, item.memory_type,
                item.content, item.importance, chat_id
            )
            added.append(mem)
        return added
    except Exception as e:
        print(f"记忆提取失败: {e}")
        return []
