# 聊天服务 - 处理聊天相关的业务逻辑

from sqlalchemy.orm import Session
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, MessageCreate


# 创建聊天
def create_chat(db: Session, project_id: str, chat_data: ChatCreate):
    new_chat = Chat(
        project_id=project_id,
        title=chat_data.title,
        model=chat_data.model
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


# 获取聊天列表
def get_chats(db: Session, project_id: str, skip: int = 0, limit: int = 20):
    chats = db.query(Chat).filter(
        Chat.project_id == project_id
    ).order_by(Chat.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Chat).filter(Chat.project_id == project_id).count()
    return chats, total


# 获取单个聊天
def get_chat(db: Session, chat_id: str, project_id: str):
    return db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.project_id == project_id
    ).first()


# 删除聊天
def delete_chat(db: Session, chat_id: str, project_id: str):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.project_id == project_id
    ).first()
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
