# 认证相关的API接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.user_service import register_user, login_user

# 创建路由
router = APIRouter(prefix="/auth", tags=["认证"])


# 注册接口
# POST /api/v1/auth/register
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    - username: 用户名
    - email: 邮箱
    - password: 密码
    """
    try:
        user = register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 登录接口
# POST /api/v1/auth/login
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    - email: 邮箱
    - password: 密码
    返回: access_token（用于后续请求认证）
    """
    try:
        access_token, user = login_user(db, user_data)
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
