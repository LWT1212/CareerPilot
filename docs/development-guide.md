# CareerPilot AI - 开发规范文档

| 项目 | 内容 |
|------|------|
| **版本控制** | Git + GitHub |
| **工作流** | GitHub Flow |
| **最后更新** | 2024-01-20 |

---

## 一、Git 工作流

### 1.1 分支策略

```
main (生产分支)
  │
  ├── develop (开发主干)
  │     │
  │     ├── feature/user-auth (功能分支)
  │     ├── feature/project-mgmt
  │     ├── feature/chat-system
  │     └── ...
  │
  └── hotfix/* (紧急修复)
```

### 1.2 分支类型

| 分支类型 | 命名规范 | 说明 |
|----------|----------|------|
| main | main | 生产分支，稳定版本 |
| develop | develop | 开发主干，最新开发版本 |
| feature | feature/* | 功能分支，开发新功能 |
| bugfix | bugfix/* | 修复分支，修复Bug |
| hotfix | hotfix/* | 紧急修复，修复生产问题 |
| release | release/* | 发布分支，准备发布版本 |

### 1.3 分支命名规范

```
feature/user-auth          # 用户认证功能
feature/project-mgmt       # 项目管理功能
feature/chat-system        # 聊天系统
feature/knowledge-rag      # 知识库RAG
feature/experience-mgmt    # 经验管理
feature/interview-mgmt     # 面试模块
feature/document-gen       # 文档生成
feature/agent-system       # Agent系统

bugfix/login-error         # 修复登录错误
bugfix/chat-timeout        # 修复聊天超时

hotfix/security-patch      # 安全补丁
```

### 1.4 工作流程

```
1. 从develop创建功能分支
   git checkout -b feature/user-auth develop

2. 开发并提交
   git add .
   git commit -m "feat(user): add login API"

3. 推送到远程
   git push origin feature/user-auth

4. 创建PR到develop
   - 标题: feat(user): 实现用户登录注册
   - 描述: 
     - 实现用户注册API
     - 实现用户登录API
     - JWT Token认证

5. Code Review（可选）

6. Merge PR

7. 功能完成后，develop合并到main并打tag
```

---

## 二、Commit 规范

### 2.1 Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 2.2 Type 类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复Bug |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试相关 |
| build | 构建工具相关 |
| ci | CI配置相关 |
| chore | 其他杂项 |
| revert | 回滚 |

### 2.3 Scope 范围

| Scope | 说明 |
|-------|------|
| user | 用户模块 |
| project | 项目模块 |
| chat | 聊天模块 |
| knowledge | 知识库模块 |
| experience | 经验模块 |
| interview | 面试模块 |
| document | 文档模块 |
| agent | Agent模块 |
| auth | 认证模块 |
| api | API层 |
| db | 数据库 |
| frontend | 前端 |
| backend | 后端 |

### 2.4 Commit 示例

```
feat(user): 实现用户注册功能

- 添加用户注册API
- 实现密码加密
- 添加用户名和邮箱唯一性验证

Closes #12
```

```
fix(chat): 修复聊天消息流式响应中断问题

- 修复SSE连接超时问题
- 添加心跳机制

Fixes #45
```

```
docs(api): 更新API接口文档

- 添加面试统计接口文档
- 更新错误码定义
```

```
refactor(knowledge): 重构文档解析逻辑

- 提取公共解析方法
- 支持更多文件格式
```

---

## 三、目录结构规范

### 3.1 项目根目录

```
CareerPilot/
├── .github/                  # GitHub配置
│   └── workflows/           # GitHub Actions
├── backend/                  # 后端代码
├── frontend/                 # 前端代码
├── docker/                   # Docker配置
├── docs/                     # 项目文档
├── scripts/                  # 脚本工具
├── .gitignore               # Git忽略文件
├── .env.example             # 环境变量示例
├── docker-compose.yml       # Docker Compose配置
├── Makefile                 # 常用命令
├── README.md                # 项目说明
└── LICENSE                  # 许可证
```

### 3.2 后端目录

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI入口
│   ├── config.py            # 配置管理
│   ├── api/                 # API路由
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic模型
│   ├── services/            # 业务逻辑
│   ├── agents/              # Agent实现
│   ├── db/                  # 数据库
│   └── utils/               # 工具函数
├── tests/                   # 测试代码
├── alembic/                 # 数据库迁移
├── alembic.ini              # Alembic配置
├── requirements.txt         # 依赖列表
├── Dockerfile               # Docker构建文件
└── .env.example             # 环境变量示例
```

### 3.3 前端目录

```
frontend/
├── src/
│   ├── api/                 # API调用
│   ├── components/          # 通用组件
│   ├── views/               # 页面视图
│   ├── stores/              # 状态管理
│   ├── router/              # 路由配置
│   ├── utils/               # 工具函数
│   ├── assets/              # 静态资源
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件
├── public/                  # 公共资源
├── package.json             # 依赖配置
├── vite.config.ts           # Vite配置
├── tsconfig.json            # TypeScript配置
├── Dockerfile               # Docker构建文件
└── nginx.conf               # Nginx配置
```

---

## 四、代码规范

### 4.1 Python 代码规范

#### 命名规范

```python
# 变量名、函数名：snake_case
user_name = "magic"
def get_user_info():
    pass

# 类名：PascalCase
class UserManager:
    pass

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DATABASE_URL = "sqlite:///./careerpilot.db"

# 私有变量/方法：前缀下划线
_private_var = "secret"
def _internal_method():
    pass

# 模块文件名：snake_case
# user_service.py
# project_manager.py
```

#### 导入规范

```python
# 标准库导入
import os
import sys
from datetime import datetime
from typing import Optional, List

# 第三方库导入
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 本地模块导入
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
```

#### 代码格式

```python
# 函数定义
def create_user(
    db: Session,
    user_data: UserCreate
) -> User:
    """创建用户"""
    # 函数体
    pass

# 类定义
class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        pass

# 异步函数
async def send_message(
    chat_id: str,
    content: str
) -> Message:
    """发送消息"""
    pass
```

#### 类型注解

```python
# 变量类型注解
user_name: str = "magic"
age: int = 25
is_active: bool = True

# 函数返回类型注解
def get_user(user_id: str) -> User:
    pass

# 可选类型
def get_user(user_id: str) -> Optional[User]:
    pass

# 列表类型
def get_users() -> List[User]:
    pass

# 字典类型
config: dict = {"key": "value"}
```

---

### 4.2 TypeScript 代码规范

#### 命名规范

```typescript
// 变量名、函数名：camelCase
const userName = "magic";
function getUserInfo(): void {
  // 函数体
}

// 类名：PascalCase
class UserManager {
  // 类体
}

// 接口名：PascalCase
interface UserData {
  id: string;
  name: string;
}

// 类型名：PascalCase
type UserRole = "admin" | "user";

// 常量：UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = "http://localhost:8000";

// 文件名：kebab-case
// user-manager.ts
// user-service.ts
```

#### 导入规范

```typescript
// 第三方库导入
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

// 本地模块导入
import { User } from "@/types/user";
import { UserService } from "@/services/user-service";
import { useAuthStore } from "@/stores/auth";

// 样式导入
import "@/styles/main.css";
```

#### 代码格式

```typescript
// 接口定义
interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
}

// 类定义
class UserService {
  private apiUrl: string;

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
  }

  async getUser(userId: string): Promise<User> {
    // 方法体
  }
}

// 组合式API
export function useUser() {
  const user = ref<User | null>(null);
  const loading = ref(false);

  const fetchUser = async (userId: string) => {
    loading.value = true;
    try {
      // 获取用户逻辑
    } finally {
      loading.value = false;
    }
  };

  return {
    user,
    loading,
    fetchUser,
  };
}
```

---

## 五、注释规范

### 5.1 Python 注释

```python
# 模块级注释
"""用户管理模块

提供用户注册、登录、信息管理等功能。
"""

# 类注释
class UserService:
    """用户服务类
    
    处理用户相关的业务逻辑，包括用户创建、查询、更新等操作。
    """
    
    pass

# 函数注释
def create_user(db: Session, user_data: UserCreate) -> User:
    """创建新用户
    
    Args:
        db: 数据库会话
        user_data: 用户创建数据
        
    Returns:
        创建的用户对象
        
    Raises:
        HTTPException: 用户名或邮箱已存在
    """
    pass
```

### 5.2 TypeScript 注释

```typescript
// 接口注释
/**
 * 用户数据接口
 */
interface User {
  /** 用户ID */
  id: string;
  /** 用户名 */
  username: string;
}

// 函数注释
/**
 * 获取用户信息
 * @param userId 用户ID
 * @returns 用户信息
 */
async function getUser(userId: string): Promise<User> {
  // 函数体
}
```

---

## 六、测试规范

### 6.1 测试目录结构

```
backend/tests/
├── __init__.py
├── conftest.py              # 测试配置
├── test_auth.py             # 认证测试
├── test_projects.py         # 项目测试
├── test_chats.py            # 聊天测试
├── test_knowledge.py        # 知识库测试
├── test_experiences.py      # 经验测试
├── test_interviews.py       # 面试测试
├── test_documents.py        # 文档测试
└── test_agents.py           # Agent测试
```

### 6.2 测试命名规范

```python
# 文件命名
test_auth.py                # 认证模块测试
test_user_service.py        # 用户服务测试

# 函数命名
def test_create_user():
    """测试创建用户"""
    pass

def test_create_user_duplicate_email():
    """测试创建用户-邮箱重复"""
    pass

def test_login_success():
    """测试登录成功"""
    pass

def test_login_wrong_password():
    """测试登录-密码错误"""
    pass
```

### 6.3 测试示例

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """测试用户注册"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_login_user():
    """测试用户登录"""
    # 先注册
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    # 登录
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
```

---

## 七、API 开发规范

### 7.1 路由命名

```python
# RESTful风格
GET    /api/v1/projects           # 获取列表
POST   /api/v1/projects           # 创建
GET    /api/v1/projects/{id}      # 获取详情
PUT    /api/v1/projects/{id}      # 更新
DELETE /api/v1/projects/{id}      # 删除

# 嵌套资源
GET    /api/v1/projects/{pid}/chats           # 项目下的聊天
POST   /api/v1/projects/{pid}/chats           # 创建聊天
GET    /api/v1/chats/{cid}/messages           # 聊天的消息
POST   /api/v1/chats/{cid}/messages           # 发送消息
```

### 7.2 请求/响应格式

```python
# 请求体
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# 响应体
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

# 列表响应
class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    size: int
```

### 7.3 错误处理

```python
from fastapi import HTTPException

# 400 Bad Request
raise HTTPException(status_code=400, detail="Invalid request")

# 401 Unauthorized
raise HTTPException(status_code=401, detail="Unauthorized")

# 404 Not Found
raise HTTPException(status_code=404, detail="User not found")

# 422 Validation Error
raise HTTPException(status_code=422, detail="Validation error")
```

---

## 八、Docker 规范

### 8.1 Dockerfile 最佳实践

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 Docker Compose 规范

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    environment:
      - DATABASE_URL=sqlite:///./careerpilot.db
    restart: unless-stopped
```

---

## 九、文档规范

### 9.1 文档目录

```
docs/
├── PRD.md                    # 产品需求文档
├── database-design.md        # 数据库设计
├── api-design.md             # API接口设计
├── architecture.md           # 架构设计
├── development-guide.md      # 开发规范（本文档）
├── deployment.md             # 部署文档
└── changelog.md              # 变更日志
```

### 9.2 文档格式

- 使用Markdown格式
- 包含目录结构
- 使用表格展示结构化数据
- 代码块使用正确的语言标识
- 包含示例代码

---

## 十、代码审查清单

### 10.1 功能检查

- [ ] 功能是否按需求实现
- [ ] 边界情况是否处理
- [ ] 错误处理是否完善
- [ ] 用户体验是否良好

### 10.2 代码质量

- [ ] 代码是否符合规范
- [ ] 命名是否清晰
- [ ] 是否有重复代码
- [ ] 是否有硬编码

### 10.3 安全检查

- [ ] 输入是否验证
- [ ] SQL注入是否防护
- [ ] XSS是否防护
- [ ] 敏感信息是否暴露

### 10.4 性能检查

- [ ] 数据库查询是否优化
- [ ] 是否有N+1问题
- [ ] 是否有内存泄漏
- [ ] 是否有不必要的计算

### 10.5 测试检查

- [ ] 单元测试是否通过
- [ ] 集成测试是否通过
- [ ] 测试覆盖率是否达标
