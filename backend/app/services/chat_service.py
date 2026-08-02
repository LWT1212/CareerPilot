# 聊天服务 - 处理聊天相关的业务逻辑
# 支持两种聊天：全局聊天（project_id=None）和项目聊天（project_id=项目ID）

from sqlalchemy.orm import Session
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, MessageCreate


# 创建聊天
def create_chat(db: Session, project_id, chat_data: ChatCreate):
    """创建聊天，project_id 为 None 时创建全局聊天"""
    new_chat = Chat(
        project_id=project_id,  # 可以是项目ID或None
        title=chat_data.title,
        model=chat_data.model
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


# 获取项目聊天列表
def get_chats(db: Session, project_id: str, skip: int = 0, limit: int = 20):
    chats = db.query(Chat).filter(
        Chat.project_id == project_id
    ).order_by(Chat.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Chat).filter(Chat.project_id == project_id).count()
    return chats, total


# 获取全局聊天列表（不属于任何项目）
def get_global_chats(db: Session, skip: int = 0, limit: int = 20):
    chats = db.query(Chat).filter(
        Chat.project_id.is_(None)
    ).order_by(Chat.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Chat).filter(Chat.project_id.is_(None)).count()
    return chats, total


# 获取单个聊天（不限定项目）
def get_chat(db: Session, chat_id: str):
    return db.query(Chat).filter(Chat.id == chat_id).first()


# 删除聊天（不限定项目）
def delete_chat(db: Session, chat_id: str):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return False
    db.delete(chat)
    db.commit()
    return True


# 发送消息
def send_message(db: Session, chat_id: str, message_data: MessageCreate):
    new_message = Message(
        chat_id=chat_id,
        role="user",
        content=message_data.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# AI回复消息
def ai_reply(db: Session, chat_id: str, content: str, agent_used: str = "coordinator"):
    new_message = Message(
        chat_id=chat_id,
        role="assistant",
        content=content,
        agent_used=agent_used
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# 获取消息列表
def get_messages(db: Session, chat_id: str, skip: int = 0, limit: int = 50):
    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    total = db.query(Message).filter(Message.chat_id == chat_id).count()
    return messages, total


# 将数据库消息转为LLM需要的格式 [{"role": "user", "content": "..."}]
def messages_to_llm_history(db: Session, chat_id: str, limit: int = 10) -> list:
    messages, _ = get_messages(db, chat_id, 0, limit)
    history = []
    for msg in messages:
        if msg.role in ("user", "assistant"):
            history.append({"role": msg.role, "content": msg.content})
    return history
