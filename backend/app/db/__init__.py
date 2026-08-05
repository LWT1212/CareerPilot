#初始化模型base，创建数据库表
#初始化会话工厂，绑定引擎，获取数据库会话

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 创建数据库引擎
# connect_args 只对SQLite需要，告诉它允许多线程访问
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
# 每次操作数据库都会创建一个会话，用完自动关闭
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类
# 所有数据库表模型都要继承这个基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用法：在API接口中作为参数使用
    例如：def get_user(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db  # yield 返回会话给调用者
    finally:
        db.close()  # 用完自动关闭


def init_db():
    """
    初始化数据库
    创建所有表（如果不存在）
    首次运行时调用
    """
    Base.metadata.create_all(bind=engine)
