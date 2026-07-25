# 用户相关的数据模型（Schema）

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 用户注册请求
# 用法：POST /api/v1/auth/register
class UserCreate(BaseModel):
    username: str  # 用户名
    email: str     # 邮箱
    password: str  # 密码


# 用户登录请求
# 用法：POST /api/v1/auth/login
class UserLogin(BaseModel):
    email: str     # 邮箱
    password: str  # 密码


# 用户响应（不包含密码，安全考虑）
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 登录响应（包含Token）
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
