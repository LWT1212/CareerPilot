# CareerPilot AI - 数据库设计文档

| 项目 | 内容 |
|------|------|
| **数据库** | SQLite（V1）→ PostgreSQL（V2） |
| **ORM** | SQLAlchemy |
| **迁移工具** | Alembic |
| **最后更新** | 2024-01-20 |

---

## 一、ER 图（实体关系）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CareerPilot AI ER Diagram                      │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │    users     │
    │──────────────│
    │ id (PK)      │
    │ username     │
    │ email        │
    │ password     │
    │ ...          │
    └──────┬───────┘
           │ 1
           │
           │ N
    ┌──────┴───────┐       ┌──────────────────┐
    │   projects   │       │  user_settings   │
    │──────────────│       │──────────────────│
    │ id (PK)      │       │ id (PK)          │
    │ owner_id(FK) │       │ user_id (FK, UQ) │
    │ name         │       │ llm_provider     │
    │ ...          │       │ ...              │
    └──────┬───────┘       └──────────────────┘
           │ 1
           │
           │ N
    ┌──────┴───────────────────────────────────────────────────────┐
    │                           │                                  │
    │ N                         │ N                                │ N
    │                           │                                  │
    │                           │                                  │
┌───┴──────────┐    ┌──────────┴────────┐    ┌──────────────────┐ │
│    chats     │    │knowledge_documents│    │   experiences    │ │
│──────────────│    │──────────────────│    │──────────────────│ │
│ id (PK)      │    │ id (PK)          │    │ id (PK)          │ │
│ project_id   │    │ project_id (FK)  │    │ project_id (FK)  │ │
│ title        │    │ filename         │    │ title            │ │
│ ...          │    │ ...              │    │ ...              │ │
└───┬──────────┘    └──────────────────┘    └──────────────────┘ │
    │ 1                                                         │
    │                                                           │
    │ N                                                         │
┌───┴──────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│   messages   │    │    interviews    │    │    documents     │ │
│──────────────│    │──────────────────│    │──────────────────│ │
│ id (PK)      │    │ id (PK)          │    │ id (PK)          │ │
│ chat_id (FK) │    │ project_id (FK)  │    │ project_id (FK)  │ │
│ role         │    │ company          │    │ doc_type         │ │
│ content      │    │ ...              │    │ ...              │ │
│ ...          │    └────────┬─────────┘    └──────────────────┘ │
└───┬──────────┘             │ 1                                 │
    │ 1                      │                                   │
    │                        │ N                                 │
    │ N               ┌──────┴─────────┐                         │
┌───┴──────────┐      │interview_questions│                       │
│agent_executions│    │──────────────────│                       │
│──────────────│    │ id (PK)          │                       │
│ id (PK)      │    │ interview_id(FK) │                       │
│ message_id   │    │ question         │                       │
│ ...          │    │ ...              │                       │
└──────────────┘    └──────────────────┘                       │
                                                                │
└───────────────────────────────────────────────────────────────┘
```

---

## 二、表结构定义

### 2.1 users（用户表）

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，自动生成 |
| username | VARCHAR(50) | 是 | 用户名，唯一 |
| email | VARCHAR(100) | 是 | 邮箱，唯一 |
| hashed_password | VARCHAR(255) | 是 | 加密后的密码 |
| avatar | VARCHAR(500) | 否 | 头像URL |
| is_active | BOOLEAN | 否 | 是否激活，默认true |
| is_superuser | BOOLEAN | 否 | 是否超级用户，默认false |
| last_login_at | TIMESTAMP | 否 | 最后登录时间 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.2 projects（项目表）

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| owner_id | UUID | 是 | 外键，关联 users.id |
| name | VARCHAR(100) | 是 | 项目名称 |
| description | TEXT | 否 | 项目描述 |
| icon | VARCHAR(50) | 否 | 项目图标 |
| status | VARCHAR(20) | 否 | 状态：active/archived/deleted |
| settings | JSONB | 否 | 项目设置（JSON） |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.3 chats（聊天表）

```sql
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(200),
    model VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_chats_project ON chats(project_id);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| project_id | UUID | 是 | 外键，关联 projects.id |
| title | VARCHAR(200) | 否 | 聊天标题 |
| model | VARCHAR(50) | 否 | 使用的模型 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.4 messages（消息表）

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    agent_used VARCHAR(50),
    tokens_used INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_messages_chat ON messages(chat_id);
CREATE INDEX idx_messages_created ON messages(created_at);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| chat_id | UUID | 是 | 外键，关联 chats.id |
| role | VARCHAR(20) | 是 | 角色：user/assistant/system |
| content | TEXT | 是 | 消息内容 |
| agent_used | VARCHAR(50) | 否 | 使用的Agent类型 |
| tokens_used | INTEGER | 否 | 消耗的Token数 |
| metadata | JSONB | 否 | 元数据（JSON） |
| created_at | TIMESTAMP | 否 | 创建时间 |

---

### 2.5 knowledge_documents（知识文档表）

```sql
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    content TEXT,
    chunks JSONB,
    embedding_status VARCHAR(20) DEFAULT 'pending',
    embedding_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_knowledge_project ON knowledge_documents(project_id);
CREATE INDEX idx_knowledge_status ON knowledge_documents(embedding_status);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| project_id | UUID | 是 | 外键，关联 projects.id |
| filename | VARCHAR(255) | 是 | 文件名 |
| file_type | VARCHAR(50) | 是 | 文件类型：pdf/docx/md/txt |
| file_path | VARCHAR(500) | 是 | 文件存储路径 |
| file_size | INTEGER | 否 | 文件大小（字节） |
| content | TEXT | 否 | 提取的纯文本内容 |
| chunks | JSONB | 否 | 分块结果 |
| embedding_status | VARCHAR(20) | 否 | 嵌入状态：pending/processing/completed/failed |
| embedding_count | INTEGER | 否 | 嵌入向量数量 |
| metadata | JSONB | 否 | 元数据 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.6 experiences（开发经验表）

```sql
CREATE TABLE experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    solution TEXT,
    tags JSONB DEFAULT '[]',
    is_pinned BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_experiences_project ON experiences(project_id);
CREATE INDEX idx_experiences_type ON experiences(type);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| project_id | UUID | 是 | 外键，关联 projects.id |
| title | VARCHAR(200) | 是 | 经验标题 |
| type | VARCHAR(50) | 是 | 类型：bug/solution/architecture/lesson/note |
| content | TEXT | 是 | 经验内容 |
| solution | TEXT | 否 | 解决方案 |
| tags | JSONB | 否 | 标签数组 |
| is_pinned | BOOLEAN | 否 | 是否置顶 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.7 interviews（面试记录表）

```sql
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    company VARCHAR(100),
    position VARCHAR(100),
    interview_date DATE,
    interviewer VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',
    overall_feedback TEXT,
    result VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_interviews_project ON interviews(project_id);
CREATE INDEX idx_interviews_date ON interviews(interview_date);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| project_id | UUID | 是 | 外键，关联 projects.id |
| company | VARCHAR(100) | 否 | 公司名称 |
| position | VARCHAR(100) | 否 | 职位 |
| interview_date | DATE | 否 | 面试日期 |
| interviewer | VARCHAR(100) | 否 | 面试官 |
| status | VARCHAR(20) | 否 | 状态：scheduled/completed/cancelled |
| overall_feedback | TEXT | 否 | 整体反馈 |
| result | VARCHAR(50) | 否 | 结果：offer/rejected/pending/ghosted |
| notes | TEXT | 否 | 备注 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.8 interview_questions（面试问题表）

```sql
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    user_answer TEXT,
    interviewer_feedback TEXT,
    category VARCHAR(100),
    difficulty VARCHAR(20),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    learning_suggestion TEXT,
    is_weak_point BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_questions_interview ON interview_questions(interview_id);
CREATE INDEX idx_questions_category ON interview_questions(category);
CREATE INDEX idx_questions_weak ON interview_questions(is_weak_point);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| interview_id | UUID | 是 | 外键，关联 interviews.id |
| question | TEXT | 是 | 面试问题 |
| user_answer | TEXT | 否 | 用户回答 |
| interviewer_feedback | TEXT | 否 | 面试官反馈 |
| category | VARCHAR(100) | 否 | 分类：Redis/系统设计/算法等 |
| difficulty | VARCHAR(20) | 否 | 难度：easy/medium/hard |
| rating | INTEGER | 否 | 评分：1-5 |
| learning_suggestion | TEXT | 否 | 学习建议 |
| is_weak_point | BOOLEAN | 否 | 是否薄弱点 |
| created_at | TIMESTAMP | 否 | 创建时间 |

---

### 2.9 documents（AI文档表）

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    doc_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    content TEXT,
    version INTEGER DEFAULT 1,
    change_reason TEXT,
    is_auto_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(doc_type);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| project_id | UUID | 是 | 外键，关联 projects.id |
| doc_type | VARCHAR(50) | 是 | 文档类型：readme/prd/star/resume/project_intro |
| title | VARCHAR(200) | 否 | 文档标题 |
| content | TEXT | 否 | 文档内容 |
| version | INTEGER | 否 | 版本号，默认1 |
| change_reason | TEXT | 否 | 修改原因 |
| is_auto_generated | BOOLEAN | 否 | 是否AI生成 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

### 2.10 agent_executions（Agent执行记录表）

```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    agent_type VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    duration_ms INTEGER,
    tokens_used INTEGER,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_agent_executions_message ON agent_executions(message_id);
CREATE INDEX idx_agent_executions_agent ON agent_executions(agent_type);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| message_id | UUID | 否 | 外键，关联 messages.id |
| agent_type | VARCHAR(50) | 是 | Agent类型：coordinator/knowledge/experience/interview/document |
| input_data | JSONB | 否 | 输入数据 |
| output_data | JSONB | 否 | 输出数据 |
| duration_ms | INTEGER | 否 | 执行时长（毫秒） |
| tokens_used | INTEGER | 否 | 消耗Token数 |
| status | VARCHAR(20) | 否 | 状态：success/failed/partial |
| error_message | TEXT | 否 | 错误信息 |
| created_at | TIMESTAMP | 否 | 创建时间 |

---

### 2.11 user_settings（用户设置表）

```sql
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    llm_provider VARCHAR(50) DEFAULT 'openai',
    llm_model VARCHAR(100) DEFAULT 'gpt-4',
    llm_api_key VARCHAR(500),
    llm_base_url VARCHAR(500),
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'zh',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| user_id | UUID | 是 | 外键，关联 users.id，唯一 |
| llm_provider | VARCHAR(50) | 否 | LLM提供商：openai/ollama |
| llm_model | VARCHAR(100) | 否 | 模型名称 |
| llm_api_key | VARCHAR(500) | 否 | API Key |
| llm_base_url | VARCHAR(500) | 否 | 自定义Base URL |
| theme | VARCHAR(20) | 否 | 主题：light/dark |
| language | VARCHAR(10) | 否 | 语言：zh/en |
| settings | JSONB | 否 | 其他设置 |
| created_at | TIMESTAMP | 否 | 创建时间 |
| updated_at | TIMESTAMP | 否 | 更新时间 |

---

## 三、关系说明

### 3.1 一对多关系

| 父表 | 子表 | 外键 | 删除规则 |
|------|------|------|----------|
| users | projects | owner_id | CASCADE |
| users | user_settings | user_id | CASCADE |
| projects | chats | project_id | CASCADE |
| projects | knowledge_documents | project_id | CASCADE |
| projects | experiences | project_id | CASCADE |
| projects | interviews | project_id | CASCADE |
| projects | documents | project_id | CASCADE |
| chats | messages | chat_id | CASCADE |
| interviews | interview_questions | interview_id | CASCADE |
| messages | agent_executions | message_id | SET NULL |

### 3.2 关系图（简化）

```
users 1 ──── N projects
users 1 ──── 1 user_settings
projects 1 ──── N chats
projects 1 ──── N knowledge_documents
projects 1 ──── N experiences
projects 1 ──── N interviews
projects 1 ──── N documents
chats 1 ──── N messages
interviews 1 ──── N interview_questions
messages 1 ──── N agent_executions
```

---

## 四、索引设计

### 4.1 索引列表

| 表 | 索引名 | 字段 | 类型 | 说明 |
|----|--------|------|------|------|
| users | idx_users_email | email | B-tree | 邮箱查询 |
| users | idx_users_username | username | B-tree | 用户名查询 |
| projects | idx_projects_owner | owner_id | B-tree | 用户项目查询 |
| projects | idx_projects_status | status | B-tree | 状态筛选 |
| chats | idx_chats_project | project_id | B-tree | 项目聊天查询 |
| messages | idx_messages_chat | chat_id | B-tree | 聊天消息查询 |
| messages | idx_messages_created | created_at | B-tree | 时间排序 |
| knowledge_documents | idx_knowledge_project | project_id | B-tree | 项目文档查询 |
| knowledge_documents | idx_knowledge_status | embedding_status | B-tree | 状态筛选 |
| experiences | idx_experiences_project | project_id | B-tree | 项目经验查询 |
| experiences | idx_experiences_type | type | B-tree | 类型筛选 |
| interviews | idx_interviews_project | project_id | B-tree | 项目面试查询 |
| interviews | idx_interviews_date | interview_date | B-tree | 日期排序 |
| interview_questions | idx_questions_interview | interview_id | B-tree | 面试问题查询 |
| interview_questions | idx_questions_category | category | B-tree | 分类筛选 |
| interview_questions | idx_questions_weak | is_weak_point | B-tree | 薄弱点筛选 |
| documents | idx_documents_project | project_id | B-tree | 项目文档查询 |
| documents | idx_documents_type | doc_type | B-tree | 类型筛选 |
| agent_executions | idx_agent_executions_message | message_id | B-tree | 消息执行查询 |
| agent_executions | idx_agent_executions_agent | agent_type | B-tree | Agent类型查询 |

### 4.2 复合索引（建议）

```sql
-- 项目下按类型和时间查询经验
CREATE INDEX idx_experiences_project_type_created 
ON experiences(project_id, type, created_at DESC);

-- 项目下按公司和日期查询面试
CREATE INDEX idx_interviews_project_company_date 
ON interviews(project_id, company, interview_date DESC);

-- 项目下按类型查询文档
CREATE INDEX idx_documents_project_type_version 
ON documents(project_id, doc_type, version DESC);
```

---

## 五、数据示例

### 5.1 用户示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "magic",
  "email": "magic@example.com",
  "hashed_password": "$2b$12$LJ3m4ys1...",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 5.2 项目示例

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "CareerPilot AI",
  "description": "基于Multi-Agent的长期项目成长助手",
  "icon": "🤖",
  "status": "active",
  "settings": {
    "default_model": "gpt-4",
    "auto_generate_docs": true
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 5.3 面试统计示例

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
    }
  ],
  "weak_areas": [
    {
      "category": "Redis",
      "avg_rating": 2.5,
      "suggestion": "建议深入学习Redis持久化机制"
    }
  ]
}
```

---

## 六、迁移策略

### 6.1 SQLite → PostgreSQL 迁移

**V1阶段**：使用SQLite，便于本地开发和测试

**V2阶段**：迁移到PostgreSQL，支持生产环境

**迁移步骤**：
1. 使用 Alembic 生成迁移脚本
2. 导出 SQLite 数据
3. 转换数据格式
4. 导入 PostgreSQL
5. 验证数据完整性

### 6.2 Alembic 配置

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlite:///./careerpilot.db

[loggers]
keys = root,sqlalchemy,alembic
```

---

## 七、性能优化建议

### 7.1 查询优化

- 使用分页查询避免大量数据加载
- 对频繁查询的字段建立索引
- 使用 JSONB 索引查询嵌套数据

### 7.2 缓存策略（V2）

- 使用 Redis 缓存热点数据
- 缓存用户会话信息
- 缓存 LLM 响应结果

### 7.3 连接池配置

```python
# SQLAlchemy 连接池配置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
```
