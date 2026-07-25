# 用户服务 - 处理用户相关的业务逻辑

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.config import settings


# 密码加密上下文
# 使用bcrypt算法加密密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 创建访问令牌
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


# 验证密码
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# 加密密码
def hash_password(password: str):
    return pwd_context.hash(password)


# 用户注册
def register_user(db: Session, user_data: UserCreate):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise ValueError("用户名已存在")

    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ValueError("邮箱已存在")

    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 用户登录
def login_user(db: Session, user_data: UserLogin):
    # 查找用户
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise ValueError("邮箱或密码错误")

    # 验证密码
    if not verify_password(user_data.password, user.hashed_password):
        raise ValueError("邮箱或密码错误")

    # 检查用户是否激活
    if not user.is_active:
        raise ValueError("账号未激活")

    # 生成Token
    access_token = create_access_token(data={"sub": user.id, "username": user.username})

    return access_token, user
