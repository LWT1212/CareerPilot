# CareerPilot AI - API 接口设计文档

| 项目 | 内容 |
|------|------|
| **API 风格** | RESTful |
| **认证方式** | JWT Bearer Token |
| **数据格式** | JSON |
| **流式响应** | SSE (Server-Sent Events) |
| **最后更新** | 2024-01-20 |

---

## 一、接口总览

### 1.1 基础信息

| 项目 | 说明 |
|------|------|
| Base URL | `http://localhost:8000/api/v1` |
| 认证方式 | `Authorization: Bearer <token>` |
| 内容类型 | `Content-Type: application/json` |
| 流式响应 | `Accept: text/event-stream` |

### 1.2 接口列表

| 模块 | 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|------|
| **认证** | /auth/register | POST | 注册 | ❌ |
| | /auth/login | POST | 登录 | ❌ |
| | /auth/refresh | POST | 刷新Token | ✅ |
| | /auth/me | GET | 获取当前用户 | ✅ |
| | /auth/me | PUT | 更新用户信息 | ✅ |
| | /auth/change-pwd | POST | 修改密码 | ✅ |
| **项目** | /projects | GET | 获取项目列表 | ✅ |
| | /projects | POST | 创建项目 | ✅ |
| | /projects/{id} | GET | 获取项目详情 | ✅ |
| | /projects/{id} | PUT | 更新项目 | ✅ |
| | /projects/{id} | DELETE | 删除项目 | ✅ |
| **聊天** | /projects/{pid}/chats | GET | 获取聊天列表 | ✅ |
| | /projects/{pid}/chats | POST | 创建聊天 | ✅ |
| | /projects/{pid}/chats/{id} | GET | 获取聊天详情 | ✅ |
| | /projects/{pid}/chats/{id} | PUT | 更新聊天 | ✅ |
| | /projects/{pid}/chats/{id} | DELETE | 删除聊天 | ✅ |
| **消息** | /chats/{cid}/messages | GET | 获取消息列表 | ✅ |
| | /chats/{cid}/messages | POST | 发送消息 | ✅ |
| **知识库** | /projects/{pid}/knowledge | GET | 获取文档列表 | ✅ |
| | /projects/{pid}/knowledge | POST | 上传文档 | ✅ |
| | /projects/{pid}/knowledge/{id} | GET | 获取文档详情 | ✅ |
| | /projects/{pid}/knowledge/{id} | DELETE | 删除文档 | ✅ |
| | /projects/{pid}/knowledge/search | POST | 知识检索 | ✅ |
| **经验** | /projects/{pid}/experiences | GET | 获取经验列表 | ✅ |
| | /projects/{pid}/experiences | POST | 创建经验 | ✅ |
| | /projects/{pid}/experiences/{id} | GET | 获取经验详情 | ✅ |
| | /projects/{pid}/experiences/{id} | PUT | 更新经验 | ✅ |
| | /projects/{pid}/experiences/{id} | DELETE | 删除经验 | ✅ |
| **面试** | /projects/{pid}/interviews | GET | 获取面试列表 | ✅ |
| | /projects/{pid}/interviews | POST | 创建面试 | ✅ |
| | /projects/{pid}/interviews/{id} | GET | 获取面试详情 | ✅ |
| | /projects/{pid}/interviews/{id} | PUT | 更新面试 | ✅ |
| | /projects/{pid}/interviews/{id} | DELETE | 删除面试 | ✅ |
| | /interviews/{id}/questions | POST | 添加面试问题 | ✅ |
| | /projects/{pid}/interviews/stats | GET | 面试统计 | ✅ |
| **文档** | /projects/{pid}/documents | GET | 获取文档列表 | ✅ |
| | /projects/{pid}/documents/{type} | GET | 获取文档内容 | ✅ |
| | /projects/{pid}/documents/{type} | PUT | 更新文档 | ✅ |
| | /projects/{pid}/documents/{type}/generate | POST | AI生成文档 | ✅ |
| **Agent** | /agents/status | GET | Agent状态 | ✅ |

---

## 二、认证模块

### 2.1 POST /api/v1/auth/register

**注册新用户**

**Request Body**:
```json
{
  "username": "magic",
  "email": "magic@example.com",
  "password": "securepass123"
}
```

**Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "magic",
  "email": "magic@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**错误响应**:
```json
// 400 Bad Request - 用户名已存在
{
  "detail": "Username already exists"
}

// 400 Bad Request - 邮箱已存在
{
  "detail": "Email already exists"
}

// 422 Unprocessable Entity - 参数验证失败
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.min_length"
    }
  ]
}
```

---

### 2.2 POST /api/v1/auth/login

**用户登录**

**Request Body**:
```json
{
  "email": "magic@example.com",
  "password": "securepass123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**错误响应**:
```json
// 401 Unauthorized - 邮箱或密码错误
{
  "detail": "Invalid email or password"
}

// 401 Unauthorized - 账号未激活
{
  "detail": "Account is not active"
}
```

---

### 2.3 POST /api/v1/auth/refresh

**刷新 Token**

**Headers**: `Authorization: Bearer <refresh_token>`

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 2.4 GET /api/v1/auth/me

**获取当前用户信息**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "magic",
  "email": "magic@example.com",
  "avatar": "https://example.com/avatar.jpg",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 2.5 PUT /api/v1/auth/me

**更新用户信息**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "username": "magic_new",
  "avatar": "https://example.com/new-avatar.jpg"
}
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "magic_new",
  "email": "magic@example.com",
  "avatar": "https://example.com/new-avatar.jpg",
  "is_active": true,
  "updated_at": "2024-01-20T15:00:00Z"
}
```

---

### 2.6 POST /api/v1/auth/change-pwd

**修改密码**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "old_password": "securepass123",
  "new_password": "newsecurepass456"
}
```

**Response (200 OK)**:
```json
{
  "message": "Password changed successfully"
}
```

---

## 三、项目模块

### 3.1 GET /api/v1/projects

**获取项目列表**

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |
| status | string | 否 | 状态筛选：active/archived/deleted |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "CareerPilot AI",
      "description": "基于Multi-Agent的长期项目成长助手",
      "icon": "🤖",
      "status": "active",
      "stats": {
        "chats_count": 15,
        "knowledge_count": 8,
        "experiences_count": 23,
        "interviews_count": 5
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

---

### 3.2 POST /api/v1/projects

**创建项目**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "CareerPilot AI",
  "description": "基于Multi-Agent的长期项目成长助手",
  "icon": "🤖"
}
```

**Response (201 Created)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "CareerPilot AI",
  "description": "基于Multi-Agent的长期项目成长助手",
  "icon": "🤖",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 3.3 GET /api/v1/projects/{project_id}

**获取项目详情**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "CareerPilot AI",
  "description": "基于Multi-Agent的长期项目成长助手",
  "icon": "🤖",
  "status": "active",
  "stats": {
    "chats_count": 15,
    "knowledge_count": 8,
    "experiences_count": 23,
    "interviews_count": 5,
    "documents_count": 6,
    "total_tokens_used": 125000
  },
  "recent_activity": [
    {
      "type": "chat",
      "title": "讨论RAG实现",
      "time": "2024-01-20T14:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:30:00Z"
}
```

---

### 3.4 PUT /api/v1/projects/{project_id}

**更新项目**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "CareerPilot AI Pro",
  "description": "更新后的描述",
  "status": "archived"
}
```

**Response (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "CareerPilot AI Pro",
  "description": "更新后的描述",
  "status": "archived",
  "updated_at": "2024-01-20T16:00:00Z"
}
```

---

### 3.5 DELETE /api/v1/projects/{project_id}

**删除项目**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "message": "Project deleted successfully"
}
```

---

## 四、聊天模块

### 4.1 GET /api/v1/projects/{project_id}/chats

**获取聊天列表**

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "讨论RAG实现方案",
      "model": "gpt-4",
      "message_count": 12,
      "last_message": {
        "content": "好的，我来帮你设计...",
        "created_at": "2024-01-20T14:30:00Z"
      },
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 15
}
```

---

### 4.2 POST /api/v1/projects/{project_id}/chats

**创建新聊天**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "讨论数据库设计",
  "model": "gpt-4"
}
```

**Response (201 Created)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "title": "讨论数据库设计",
  "model": "gpt-4",
  "message_count": 0,
  "created_at": "2024-01-20T15:00:00Z"
}
```

---

### 4.3 GET /api/v1/projects/{project_id}/chats/{chat_id}

**获取聊天详情**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "title": "讨论RAG实现方案",
  "model": "gpt-4",
  "message_count": 12,
  "created_at": "2024-01-20T10:00:00Z"
}
```

---

### 4.4 PUT /api/v1/projects/{project_id}/chats/{chat_id}

**更新聊天**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "更新后的标题"
}
```

**Response (200 OK)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "title": "更新后的标题",
  "updated_at": "2024-01-20T16:00:00Z"
}
```

---

### 4.5 DELETE /api/v1/projects/{project_id}/chats/{chat_id}

**删除聊天**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "message": "Chat deleted successfully"
}
```

---

## 五、消息模块

### 5.1 GET /api/v1/chats/{chat_id}/messages

**获取消息列表**

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认50 |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "role": "user",
      "content": "帮我分析一下这个Bug的原因",
      "created_at": "2024-01-20T14:30:00Z"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440005",
      "role": "assistant",
      "content": "根据代码分析，这个Bug的原因是...",
      "agent_used": "knowledge",
      "tokens_used": 256,
      "created_at": "2024-01-20T14:30:05Z"
    }
  ],
  "total": 12
}
```

---

### 5.2 POST /api/v1/chats/{chat_id}/messages

**发送消息（支持流式响应）**

**Headers**:
- `Authorization: Bearer <token>`
- `Accept: text/event-stream`（流式响应时）

**Request Body**:
```json
{
  "content": "帮我分析一下用户系统的数据库设计",
  "stream": true
}
```

#### 非流式响应 (stream=false)

**Response (200 OK)**:
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440006",
  "role": "assistant",
  "content": "根据项目知识库中的最佳实践，建议的用户表设计如下：\n\n1. id: UUID 主键\n2. username: VARCHAR(50) 用户名\n3. email: VARCHAR(100) 邮箱\n...",
  "agent_used": "coordinator",
  "tokens_used": 512,
  "created_at": "2024-01-20T15:00:00Z"
}
```

#### 流式响应 (stream=true)

**Response (SSE)**:
```
data: {"type": "message_start", "message_id": "880e8400-e29b-41d4-a716-446655440007"}

data: {"type": "agent_start", "agent": "coordinator"}

data: {"type": "thinking", "content": "分析用户意图：请求数据库设计建议"}

data: {"type": "agent_end", "agent": "coordinator"}

data: {"type": "agent_start", "agent": "knowledge"}

data: {"type": "chunk", "content": "根据项目知识库中的最佳实践..."}

data: {"type": "chunk", "content": "建议的用户表设计如下："}

data: {"type": "chunk", "content": "\n\n1. id: UUID 主键"}

data: {"type": "chunk", "content": "\n2. username: VARCHAR(50) 用户名"}

data: {"type": "agent_end", "agent": "knowledge"}

data: {"type": "done", "message_id": "880e8400-e29b-41d4-a716-446655440007", "tokens_used": 256}
```

**SSE 事件类型**：

| 类型 | 说明 |
|------|------|
| message_start | 消息开始 |
| thinking | 思考过程（可选） |
| agent_start | Agent开始执行 |
| chunk | 内容片段 |
| agent_end | Agent执行完成 |
| error | 错误信息 |
| done | 消息完成 |

---

## 六、知识库模块

### 6.1 GET /api/v1/projects/{project_id}/knowledge

**获取知识文档列表**

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |
| status | string | 否 | 状态筛选：pending/processing/completed/failed |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440008",
      "filename": "redis-guide.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "embedding_status": "completed",
      "embedding_count": 45,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 8,
  "stats": {
    "total_documents": 8,
    "total_embeddings": 320,
    "by_type": {
      "pdf": 5,
      "md": 2,
      "txt": 1
    }
  }
}
```

---

### 6.2 POST /api/v1/projects/{project_id}/knowledge

**上传知识文档**

**Headers**: `Authorization: Bearer <token>`

**Request Body**: `multipart/form-data`
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | PDF/Word/Markdown/TXT文件 |

**Response (202 Accepted)**:
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440009",
  "filename": "redis-guide.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "embedding_status": "processing",
  "message": "文档已上传，正在解析和生成向量..."
}
```

---

### 6.3 GET /api/v1/projects/{project_id}/knowledge/{doc_id}

**获取文档详情**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440008",
  "filename": "redis-guide.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "content": "Redis是一个开源的内存数据结构存储系统...",
  "chunks_count": 12,
  "embedding_status": "completed",
  "embedding_count": 45,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### 6.4 DELETE /api/v1/projects/{project_id}/knowledge/{doc_id}

**删除知识文档**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "message": "Document deleted successfully"
}
```

---

### 6.5 POST /api/v1/projects/{project_id}/knowledge/search

**知识检索（RAG）**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "query": "Redis持久化机制",
  "top_k": 5,
  "filter_type": "pdf"
}
```

**Response (200 OK)**:
```json
{
  "results": [
    {
      "document_id": "990e8400-e29b-41d4-a716-446655440008",
      "filename": "redis-guide.pdf",
      "chunk_index": 3,
      "content": "Redis支持两种持久化方式：RDB和AOF。RDB是快照方式，AOF是日志追加方式...",
      "score": 0.92,
      "metadata": {
        "page": 15,
        "section": "持久化"
      }
    }
  ],
  "query": "Redis持久化机制",
  "total_results": 5
}
```

---

## 七、经验模块

### 7.1 GET /api/v1/projects/{project_id}/experiences

**获取经验列表**

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |
| type | string | 否 | 类型筛选：bug/solution/architecture/lesson/note |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440010",
      "title": "Docker部署权限问题",
      "type": "bug",
      "content": "Docker容器内无法写入文件，报错Permission denied",
      "solution": "将用户加入docker group: sudo usermod -aG docker $USER",
      "tags": ["docker", "permissions"],
      "is_pinned": true,
      "created_at": "2024-01-18T10:00:00Z"
    }
  ],
  "total": 23,
  "stats": {
    "by_type": {
      "bug": 8,
      "solution": 10,
      "architecture": 3,
      "lesson": 2
    }
  }
}
```

---

### 7.2 POST /api/v1/projects/{project_id}/experiences

**创建经验**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Docker部署权限问题",
  "type": "bug",
  "content": "Docker容器内无法写入文件，报错Permission denied",
  "solution": "将用户加入docker group: sudo usermod -aG docker $USER",
  "tags": ["docker", "permissions"]
}
```

**Response (201 Created)**:
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440011",
  "title": "Docker部署权限问题",
  "type": "bug",
  "content": "Docker容器内无法写入文件，报错Permission denied",
  "solution": "将用户加入docker group: sudo usermod -aG docker $USER",
  "tags": ["docker", "permissions"],
  "is_pinned": false,
  "created_at": "2024-01-20T15:00:00Z"
}
```

---

### 7.3 GET /api/v1/projects/{project_id}/experiences/{exp_id}

**获取经验详情**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**: 同创建响应

---

### 7.4 PUT /api/v1/projects/{project_id}/experiences/{exp_id}

**更新经验**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "solution": "更新后的解决方案",
  "is_pinned": true
}
```

**Response (200 OK)**: 同创建响应，updated_at 更新

---

### 7.5 DELETE /api/v1/projects/{project_id}/experiences/{exp_id}

**删除经验**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "message": "Experience deleted successfully"
}
```

---

## 八、面试模块

### 8.1 GET /api/v1/projects/{project_id}/interviews

**获取面试列表**

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |
| company | string | 否 | 公司筛选 |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440012",
      "company": "字节跳动",
      "position": "后端工程师",
      "interview_date": "2024-01-20",
      "status": "completed",
      "result": "offer",
      "question_count": 8,
      "avg_rating": 3.5,
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 10
}
```

---

### 8.2 POST /api/v1/projects/{project_id}/interviews

**创建面试记录**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "company": "字节跳动",
  "position": "后端工程师",
  "interview_date": "2024-01-20",
  "interviewer": "张工",
  "status": "completed",
  "result": "offer",
  "overall_feedback": "项目经验丰富，算法需要加强"
}
```

**Response (201 Created)**:
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440013",
  "company": "字节跳动",
  "position": "后端工程师",
  "interview_date": "2024-01-20",
  "interviewer": "张工",
  "status": "completed",
  "result": "offer",
  "overall_feedback": "项目经验丰富，算法需要加强",
  "created_at": "2024-01-20T10:00:00Z"
}
```

---

### 8.3 GET /api/v1/projects/{project_id}/interviews/{interview_id}

**获取面试详情**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440012",
  "company": "字节跳动",
  "position": "后端工程师",
  "interview_date": "2024-01-20",
  "interviewer": "张工",
  "status": "completed",
  "result": "offer",
  "overall_feedback": "项目经验丰富，算法需要加强",
  "questions": [
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440014",
      "question": "Redis的持久化机制有哪些？",
      "user_answer": "RDB和AOF",
      "category": "Redis",
      "difficulty": "medium",
      "rating": 4
    }
  ],
  "created_at": "2024-01-20T10:00:00Z"
}
```

---

### 8.4 PUT /api/v1/projects/{project_id}/interviews/{interview_id}

**更新面试记录**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "overall_feedback": "更新后的反馈",
  "result": "offer"
}
```

---

### 8.5 DELETE /api/v1/projects/{project_id}/interviews/{interview_id}

**删除面试记录**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "message": "Interview deleted successfully"
}
```

---

### 8.6 POST /api/v1/interviews/{interview_id}/questions

**添加面试问题**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "question": "Redis的持久化机制有哪些？",
  "user_answer": "RDB和AOF，RDB是快照，AOF是日志追加",
  "interviewer_feedback": "回答基本正确，但没有提到混合持久化",
  "category": "Redis",
  "difficulty": "medium",
  "rating": 4,
  "learning_suggestion": "建议了解Redis混合持久化机制"
}
```

**Response (201 Created)**:
```json
{
  "id": "cc0e8400-e29b-41d4-a716-446655440015",
  "interview_id": "bb0e8400-e29b-41d4-a716-446655440012",
  "question": "Redis的持久化机制有哪些？",
  "user_answer": "RDB和AOF，RDB是快照，AOF是日志追加",
  "interviewer_feedback": "回答基本正确，但没有提到混合持久化",
  "category": "Redis",
  "difficulty": "medium",
  "rating": 4,
  "learning_suggestion": "建议了解Redis混合持久化机制",
  "is_weak_point": false,
  "created_at": "2024-01-20T11:00:00Z"
}
```

---

### 8.7 GET /api/v1/projects/{project_id}/interviews/stats

**面试统计**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "summary": {
    "total_interviews": 10,
    "total_questions": 85,
    "average_rating": 3.2,
    "offer_rate": 0.4
  },
  "by_company": [
    {
      "company": "字节跳动",
      "count": 3,
      "offer_count": 2,
      "avg_rating": 3.5
    },
    {
      "company": "阿里巴巴",
      "count": 2,
      "offer_count": 1,
      "avg_rating": 3.0
    }
  ],
  "by_category": [
    {
      "category": "Redis",
      "question_count": 12,
      "avg_rating": 2.5,
      "weak_points": ["持久化机制", "集群部署"]
    },
    {
      "category": "系统设计",
      "question_count": 8,
      "avg_rating": 3.0,
      "weak_points": ["高并发处理"]
    }
  ],
  "weak_areas": [
    {
      "category": "Redis",
      "avg_rating": 2.5,
      "suggestion": "建议深入学习Redis持久化机制和集群部署"
    }
  ],
  "timeline": [
    {
      "date": "2024-01-15",
      "company": "字节跳动",
      "result": "offer",
      "rating": 3.5
    },
    {
      "date": "2024-01-18",
      "company": "阿里巴巴",
      "result": "rejected",
      "rating": 3.0
    }
  ]
}
```

---

## 九、文档模块

### 9.1 GET /api/v1/projects/{project_id}/documents

**获取文档列表**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440016",
      "doc_type": "readme",
      "title": "README.md",
      "version": 5,
      "is_auto_generated": true,
      "updated_at": "2024-01-20T10:00:00Z"
    },
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440017",
      "doc_type": "prd",
      "title": "PRD.md",
      "version": 3,
      "is_auto_generated": false,
      "updated_at": "2024-01-19T15:00:00Z"
    }
  ],
  "total": 6
}
```

---

### 9.2 GET /api/v1/projects/{project_id}/documents/{doc_type}

**获取指定类型文档**

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:
| 参数 | 说明 |
|------|------|
| doc_type | readme/prd/star/resume/project_intro |

**Response (200 OK)**:
```json
{
  "id": "dd0e8400-e29b-41d4-a716-446655440016",
  "doc_type": "readme",
  "title": "README.md",
  "content": "# CareerPilot AI\n\n基于Multi-Agent的长期项目成长助手...\n\n## 功能特性\n\n- 项目管理\n- 智能聊天\n- 知识库RAG\n...",
  "version": 5,
  "change_reason": "更新了技术架构说明",
  "is_auto_generated": true,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

---

### 9.3 PUT /api/v1/projects/{project_id}/documents/{doc_type}

**更新文档**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "content": "# CareerPilot AI Pro\n\n更新后的内容...",
  "change_reason": "手动更新"
}
```

**Response (200 OK)**:
```json
{
  "id": "dd0e8400-e29b-41d4-a716-446655440016",
  "doc_type": "readme",
  "title": "README.md",
  "content": "# CareerPilot AI Pro\n\n更新后的内容...",
  "version": 6,
  "change_reason": "手动更新",
  "is_auto_generated": false,
  "updated_at": "2024-01-20T16:00:00Z"
}
```

---

### 9.4 POST /api/v1/projects/{project_id}/documents/{doc_type}/generate

**AI 生成/更新文档**

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "instruction": "根据项目知识库生成README，突出Multi-Agent特色"
}
```

**Response (200 OK)**:
```json
{
  "id": "dd0e8400-e29b-41d4-a716-446655440018",
  "doc_type": "readme",
  "title": "README.md",
  "content": "# CareerPilot AI\n\n## 简介\n\nCareerPilot AI 是一款基于 Multi-Agent 的长期项目成长助手...\n\n## 核心功能\n\n### Multi-Agent 协同\n\n- **Coordinator Agent**: 统一调度\n- **Knowledge Agent**: 知识检索\n- **Experience Agent**: 经验整理\n...",
  "version": 7,
  "change_reason": "AI根据知识库自动生成",
  "is_auto_generated": true,
  "updated_at": "2024-01-20T17:00:00Z"
}
```

---

## 十、Agent 模块

### 10.1 GET /api/v1/agents/status

**获取 Agent 状态**

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "agents": [
    {
      "type": "coordinator",
      "name": "Coordinator Agent",
      "status": "ready",
      "description": "统一调度，理解用户意图",
      "capabilities": ["意图识别", "任务规划", "Agent调度"]
    },
    {
      "type": "knowledge",
      "name": "Knowledge Agent",
      "status": "ready",
      "description": "RAG检索，技术问答",
      "capabilities": ["文档检索", "技术问答", "文档总结"]
    },
    {
      "type": "experience",
      "name": "Experience Agent",
      "status": "ready",
      "description": "开发经验整理",
      "capabilities": ["经验整理", "成长记录", "问题分类"]
    },
    {
      "type": "interview",
      "name": "Interview Agent",
      "status": "ready",
      "description": "面试分析，成长建议",
      "capabilities": ["面试分析", "成长轨迹", "高频问题统计"]
    },
    {
      "type": "document",
      "name": "Document Agent",
      "status": "ready",
      "description": "文档自动生成",
      "capabilities": ["README生成", "PRD生成", "简历优化"]
    }
  ]
}
```

---

## 十一、错误码定义

### 11.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 202 | 已接受（异步处理） |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

### 11.2 业务错误码

| 错误码 | 说明 |
|--------|------|
| AUTH_001 | 用户名已存在 |
| AUTH_002 | 邮箱已存在 |
| AUTH_003 | 密码错误 |
| AUTH_004 | 账号未激活 |
| AUTH_005 | Token已过期 |
| PROJ_001 | 项目不存在 |
| PROJ_002 | 项目名称重复 |
| CHAT_001 | 聊天不存在 |
| KNOW_001 | 文档不存在 |
| KNOW_002 | 文档格式不支持 |
| KNOW_003 | 文档解析失败 |
| EXP_001 | 经验不存在 |
| INTER_001 | 面试记录不存在 |
| INTER_002 | 面试问题不存在 |
| DOC_001 | 文档不存在 |
| DOC_002 | 文档类型不支持 |
| AGENT_001 | Agent执行失败 |

### 11.3 错误响应格式

```json
{
  "detail": "错误描述",
  "error_code": "AUTH_001",
  "errors": [
    {
      "loc": ["body", "username"],
      "msg": "Username already exists",
      "type": "value_error"
    }
  ]
}
```

---

## 十二、分页规范

### 12.1 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| size | integer | 20 | 每页数量 |

### 12.2 响应格式

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

---

## 十三、认证规范

### 13.1 Token 格式

```
Authorization: Bearer <access_token>
```

### 13.2 Token 有效期

| Token 类型 | 有效期 |
|------------|--------|
| access_token | 30 分钟 |
| refresh_token | 7 天 |

### 13.3 Token 刷新流程

```
access_token 过期 → 使用 refresh_token → 获取新的 access_token
refresh_token 过期 → 重新登录
```
