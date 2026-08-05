# CareerPilot AI - 优化路线图与记录

> 本文件记录 V1 之后的全部优化项。每完成一项优化，就在对应任务下方更新**优化方案、详细步骤、遇到的问题**。
> 最后更新: 2026-08-02

---

## 当前系统运行流程（V1 基线）

```
用户输入
   │
   ▼
┌────────────────────────────────────────────────────┐
│ 前端 Vue3 (ChatGPT风格)                            │
│  - 左侧: 全局聊天 + 项目展开(聊天/文档/上传)      │
│  - 中间: 聊天窗口 (SSE流式)                       │
│  - 右侧: Project Context面板                      │
└──────────────────────┬─────────────────────────────┘
                       │ HTTP (JWT认证, Bearer Token)
                       ▼
┌────────────────────────────────────────────────────┐
│ Nginx (生产) 或 Vite代理 (开发)                    │
│  - / → 前端静态文件                                │
│  - /api → 后端                                     │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ FastAPI 路由层 (/api/v1)                           │
│  auth / projects / chats / knowledge /             │
│  experiences / interviews / documents / agents     │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 聊天消息处理 (chats.py)                            │
│  非流式: run_agent() → LangGraph多智能体           │
│  流式:   stream_completion() → 直接LLM (未走Agent) │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ LangGraph 多智能体工作流 (langgraph_workflow.py)   │
│  coordinator (LLM意图识别)                         │
│     │ 条件路由                                     │
│     ├─→ knowledge   (RAG检索+回答)                 │
│     ├─→ experience  (仅文字建议, 不写库)           │
│     ├─→ interview   (仅文字建议, 不读库)           │
│     ├─→ document    (仅文字建议, 不保存)           │
│     └─→ chat        (普通对话)                     │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ LLM服务层 (llm_service.py)                         │
│  OpenAI / Ollama 双引擎                            │
│  + RAG (rag_service.py: ChromaDB嵌入式)            │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 数据层: SQLite (SQLAlchemy) + ChromaDB + 文件系统  │
└────────────────────────────────────────────────────┘
```

### 当前 V1 已知短板

| 环节 | 现状 | 问题 |
|------|------|------|
| 流式接口 | 直接调LLM | 没走多智能体，与普通接口行为不一致 |
| 经验Agent | 只返回文字 | 不真实写入 experiences 表 |
| 面试Agent | 只返回文字 | 不读取真实面试记录 |
| 文档Agent | 只返回文字 | 不保存文档 |
| Agent执行 | 无记录 | agent_executions 表闲置 |
| 意图识别 | 文本匹配 | 不稳定，无结构化输出 |
| 上下文 | 固定最近10条 | 无裁剪/摘要，长对话超token |
| 项目感知 | 仅知识库RAG | 不感知经验/面试/文档数据 |
| 记忆 | 无 | 每次对话"失忆" |
| MCP/Skill | 无 | V2规划 |

---

## 优化路线图总览

### 第一批：多智能体核心（V1.1）
| 任务 | 内容 |
|------|------|
| [x] T13 O1 | Agent执行过程记录 + Agent真实工具 + 流式接入多智能体 |
| [x] T14 O2 | 结构化意图识别 + 项目上下文注入 + 上下文裁剪 |

### 第二批：记忆与成长（V1.2）
| 任务 | 内容 |
|------|------|
| [ ] T15 O3 | 长期记忆系统 |
| [ ] T16 O4 | 主动成长能力（薄弱点学习计划） |

### 第三批：生态扩展（V2）
| 任务 | 内容 |
|------|------|
| [ ] T17 O5 | MCP工具接入 + 内置工具集 |
| [ ] T18 O6 | Skill系统 + Prompt模板库 |
| [ ] T19 O7 | 工程优化（PostgreSQL/异步/测试） |

---

## T13 O1: Agent执行过程记录 + Agent真实工具 + 流式接入多智能体

**状态**: ✅ 已完成 (2026-08-02)

### 优化目标
1. Agent 能真正操作数据库（记录经验、读取面试、保存文档）
2. Agent 执行过程被记录并展示（agent_executions 表 + API）
3. 流式接口也走多智能体

### 详细步骤

**A. Agent真实工具（agent_tools.py）**
1. 新建 `backend/app/agents/agent_tools.py`，创建6个工具：
   - `save_experience` 写经验（title/type/content/solution）
   - `get_recent_experiences` 查最近经验
   - `get_interview_stats` 面试统计+薄弱点
   - `save_document` 保存/更新文档
   - `get_document` 查询文档
   - `search_project_knowledge` 语义检索知识库
2. 定义 `TOOL_DESCRIPTIONS` 工具描述字典（供LLM判断调用）

**B. LangGraph接入工具（langgraph_workflow.py 重构）**
1. 状态扩展：`db`（数据库会话）+ `execution_log`
2. 新增 `_agent_with_tools()` 通用Agent执行器：
   - LLM判断是否需要工具（TOOL:工具名(参数=值) 或 NONE）
   - 需要 → 解析参数 → 调用工具 → 基于结果回复
   - 不需要 → 纯咨询回复（自动注入项目上下文）
3. 各Agent节点改为使用 `_agent_with_tools`：
   - knowledge → search_project_knowledge
   - experience → save/get_recent_experiences
   - interview → get_interview_stats
   - document → save/get_document
4. `_build_project_context()`：回复时注入项目经验+面试薄弱点+知识库

**C. 执行过程记录（agent_executions）**
1. 新建 `models/agent_execution.py`（AgentExecution模型）
2. `_record_execution()` 记录 agent_type/input/output/duration_ms/status
3. agents API 新增 `GET /api/v1/agents/executions`

**D. 聊天接口传db**
1. `chats.py` send 接口调用 `run_agent(..., db)` 传入数据库会话

**E. 流式接入多智能体（/stream）**
1. 先执行意图识别（复用coordinator逻辑）
2. 发送 `agent` SSE事件（coordinator识别结果）
3. 需要工具时执行工具并发送 `tool` 事件
4. 最终回复 `stream_completion` 流式输出
5. 发送 `done` 事件

### 遇到的问题
| 问题 | 解决 |
|------|------|
| Agent执行耗时较长（小模型工具判断慢） | 接受，T14结构化输出后改善 |
| 意图识别小模型不准（Redis是什么→document） | T14 O2 解决（结构化识别） |
| 工具参数解析靠文本分割，可能丢参数 | T14 O2 用结构化输出 |
| type字段工具解析时未传导致默认lesson | 同上 |

---

## T14 O2: 结构化意图识别 + 项目上下文注入 + 上下文裁剪

**状态**: ✅ 已完成 (2026-08-02)

### 优化目标
1. 结构化意图识别（解决小模型误判，Redis是什么→document）
2. 结构化工具调用（解决参数丢失，type字段）
3. 项目上下文按Agent类型注入
4. 上下文裁剪（长对话token管理）

### 详细步骤

**A. 结构化Schema（agent_schemas.py）**
1. 新建 `backend/app/agents/agent_schemas.py`，创建4个Pydantic模型：
   - `IntentOutput`: intent(Literal) + confidence(0-1) + project_related
   - `ToolCallOutput`: use_tool(bool) + tool(名字) + arguments(dict)
   - `SummaryOutput`: summary
   - `ExperienceExtractOutput`: title/exp_type/content/solution

**B. 结构化输出函数（llm_service.py）**
1. 新增 `structured_completion()`：
   - 提示词用**文字描述字段**（不贴完整schema JSON，小模型生成量小、快）
   - 让LLM输出纯JSON → Pydantic解析
   - 清理markdown代码块
2. 新增 `_schema_field_description()`：从Pydantic模型生成简洁字段描述

**C. LangGraph改造（langgraph_workflow.py）**
1. coordinator_node：用 `structured_completion(IntentOutput)` 识别意图
   - 置信度<0.4时兜底为chat
2. _agent_with_tools：用 `structured_completion(ToolCallOutput)` 判断工具
   - 使用schema的arguments字段（不再文本分割，参数不丢失）
   - save_experience直接映射arguments到工具参数
3. _build_project_context：按Agent类型注入不同上下文
   - experience → 最近经验(5条)
   - interview → 面试统计+薄弱点
   - knowledge → RAG检索(3条)
   - document → 现有文档列表

**D. 上下文裁剪（chat_service.py）**
1. messages_to_llm_history：单条消息超过2000字符截断

**E. 阿里云接入**
1. config.py 新增 `OPENAI_BASE_URL`
2. llm_service openai分支：有base_url时使用自定义端点
3. .env 切换：LLM_PROVIDER=openai + 阿里云key + qwen模型 + dashscope base_url

### 遇到的问题
| 问题 | 解决 |
|------|------|
| 本地3b小模型生成JSON极慢（30-60s/次，串行超时） | 切换到阿里云qwen模型（4-6秒/次） |
| 完整schema JSON塞提示词导致生成慢 | 改用文字描述字段（_schema_field_description） |
| .env中文注释缺#号导致dotenv解析警告 | 补上#注释符 |
| 工具参数曾丢失type字段 | ToolCallOutput.arguments结构化传递 |
| save_experience曾多一次LLM提取调用 | 直接复用ToolCallOutput.arguments |

---

## T15 O3: 长期记忆系统

**状态**: ⏳ 待开始

### 优化目标
_（待填写）_

### 详细步骤
_（实施后填写）_

### 遇到的问题
_（实施后填写）_

---

## T16 O4: 主动成长能力

**状态**: ⏳ 待开始

### 优化目标
_（待填写）_

### 详细步骤
_（实施后填写）_

### 遇到的问题
_（实施后填写）_

---

## T17 O5: MCP工具接入 + 内置工具集

**状态**: ⏳ 待开始

### 优化目标
_（待填写）_

### 详细步骤
_（实施后填写）_

### 遇到的问题
_（实施后填写）_

---

## T18 O6: Skill系统 + Prompt模板库

**状态**: ⏳ 待开始

### 优化目标
_（待填写）_

### 详细步骤
_（实施后填写）_

### 遇到的问题
_（实施后填写）_

---

## T19 O7: 工程优化

**状态**: ⏳ 待开始

### 优化目标
_（待填写）_

### 详细步骤
_（实施后填写）_

### 遇到的问题
_（实施后填写）_
