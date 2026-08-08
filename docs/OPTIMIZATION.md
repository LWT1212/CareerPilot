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
| [x] T15 O3 | 长期记忆系统 |
| [ ] T16 O4 | 主动成长能力（薄弱点学习计划） |

### 第三批：生态扩展（V2）
| 任务 | 内容 |
|------|------|
| [x] T17 O5 | MCP工具接入 + 内置工具集 |
| [x] T18 O6 | Skill系统 + Prompt模板库 |
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

**状态**: ✅ 已完成 (2026-08-02)

### 优化目标
让AI跨会话记住项目：决策/进度/问题/偏好，不再"每次都是新开始"

### 详细步骤

**S1. 建表**
1. `models/project_memory.py`：ProjectMemory（memory_type: decision/progress/problem/preference, content, importance 1-5, source_chat_id）
2. `models/chat_summary.py`：ChatSummary（chat_id, summary）
3. 注册到 models/__init__.py

**S2. 记忆服务（memory_service.py）**
1. `add_memory()`：写入+去重（同项目+同类型+前50字符相同跳过）
2. `get_project_memories()`：按重要度降序读取
3. `get_recent_summaries()`：读取对话摘要
4. `build_memory_prompt()`：组装记忆注入提示词
5. `extract_memories_from_messages()`：LLM从对话提取记忆（async）
6. `MemoriesExtractOutput` schema（嵌套 MemoryItem：type/content/importance）

**S3. 沉淀触发**
1. chats.py send接口：每5条消息触发 `extract_memories_from_messages`

**S4. 召回注入**
1. `_agent_with_tools`：开头注入 build_memory_prompt 结果
2. chat_node：注入项目记忆（之前漏了）
3. 工具无结果时 `_answer_with_memory()`：注入记忆再回答
4. 新增 `GET /projects/{id}/memories` 查询API

### 遇到的问题
| 问题 | 解决 |
|------|------|
| import错误 app.models.message | 改为 app.models.chat |
| 嵌套schema字段描述不全（memory_type枚举丢失） | _schema_field_description支持嵌套+Literal枚举 |
| 工具返回list时 tool_result.get崩溃 | 兼容dict/list/空 三种返回 |
| chat_node不注入记忆 | chat_node单独加记忆注入 |
| 知识Agent查询无结果不引用记忆 | 工具无结果时_answer_with_memory兜底 |

### 验证
- 沉淀：对话提取4条记忆（decision/preference/problem/progress）✅
- 召回：新会话问"前端框架"→ AI回答"Vue3" ✅

---

## T16 O4: 主动成长能力

**状态**: ✅ 已完成 (2026-08-02)

### 优化目标
AI主动驱动成长（PRD核心）：薄弱点学习计划+文档更新提醒+知识库影响分析

### 详细步骤

**S1. 建表**
1. `models/learning_plan.py`：LearningPlan（category, title, content, weak_count, status）
2. `models/notification.py`：Notification（ntype: weakness/doc_update/knowledge_impact, is_read）

**S2. 主动分析服务（proactive_service.py）**
1. `analyze_interview_weakness()`：统计rating<=2的面试问题→同类>=2次为薄弱→LLM生成学习计划
2. `check_document_updates()`：读决策/进度记忆→判断是否需要更新文档
3. `analyze_knowledge_impact()`：分析新上传文档对已有方案的影响
4. `get_learning_plans()/get_notifications()/mark_notification_read()` 查询API

**S3. 3个触发点**
1. 面试问题新增 → 薄弱点分析（interviews.py）
2. 记忆沉淀后 → 文档更新检查（chats.py）
3. 知识库上传 → 影响分析（knowledge.py）

**S4. API**
1. `GET /projects/{id}/learning-plans`
2. `GET /projects/{id}/notifications`（支持unread_only）
3. `POST /projects/{id}/notifications/{nid}/read`

### 遇到的问题
| 问题 | 解决 |
|------|------|
| 提醒重复创建 | 同项目同类别未读提醒去重 |

### 验证
- 3个Redis弱问题(rating=2) → 自动生成"Redis核心机制与高可用架构突破计划" + 薄弱提醒 ✅

---

## T17 O5: MCP工具接入 + 内置工具集

**状态**: ✅ S1-S3完成（S4测试待补）(2026-08-06)

### 优化目标
让 Agent 通过 MCP（Model Context Protocol）调用外部工具：GitHub查询/网页搜索/文件读取

### 详细步骤

**S1. 安装 mcp 库**
1. `pip install mcp`（装的是 2.0.0，API 与 1.x 不同）

**S2. 创建 MCP 服务器（mcp_server.py）**
1. 工具1 `github_repo_info`: GitHub公开API查询仓库（无需token）
2. 工具2 `read_local_file`: 读取本地文件（前3000字符）
3. 工具3 `web_search`: DuckDuckGo免费网页搜索（无需API key）
4. mcp 2.0 API：`from mcp.server.mcpserver import MCPServer` + `@mcp.tool()`
5. 启动：`mcp.run(transport="stdio")`（stdio协议，JSON-RPC通信）
6. 验证：stdio初始化握手返回 serverInfo

**S3. MCP客户端接入Agent（mcp_client_service.py）**
1. `call_mcp_tool()`: 用 `stdio_client + ClientSession` 启动子进程调用工具
2. 封装3个 async 工具函数（github_repo_info/web_search/read_local_file）
3. agent_tools.py 注册到 TOOLS/TOOL_DESCRIPTIONS
4. knowledge Agent 的 tool_map 集成 github_repo_info + web_search
5. `_agent_with_tools` 支持 async 工具（`inspect.iscoroutine` + await）

### 遇到的问题
| 问题 | 解决 |
|------|------|
| mcp 2.0 无 mcp.server.fastmcp 模块 | 改用 `MCPServer`（新API） |
| command="python" 找不到解释器 | 用 `sys.executable` |
| asyncio.run() 不能在运行中的事件循环调用 | MCP工具改 async + Agent await 协程 |
| 装 mcp 时 starlette 被升级到 1.4.1 | 降回 0.35.1（fastapi 0.109 兼容） |

### 验证
- MCP服务器stdio握手成功 ✅
- Agent 问"查GitHub fastapi仓库" → 调用MCP工具 → 返回真实数据（10万+star） ✅

---

## T18 O6: Skill系统 + Prompt模板库

**状态**: ✅ 已完成（经验沉淀Skill）(2026-08-06)

### 优化目标
给Agent预置"专业技能包"（Skill）：触发词匹配→专属逻辑执行

### 详细步骤

**S1. Skill框架（skills/目录）**
1. `base.py`：Skill抽象基类（name/description/execute）
2. `__init__.py`：空模块
3. `skills_manager.py`：SkillsManager类
   - register() 注册
   - match() 关键词触发匹配
   - execute() 执行
   - 全局单例 + register_all_skills()

**S2. 第一个Skill（experience_curator.py）**
1. ExperienceCurator（经验沉淀师）：
   - 组装"问题+最近AI回答"上下文
   - LLM结构化提取（ExperienceExtractOutput）
   - 调用 save_experience 写入 experiences 表
   - 返回确认信息

**S3. 接入聊天（chats.py）**
1. 手动触发：send接口先 match() → 命中Skill则执行作为回复（agent_used=skill:xxx）
2. 自动沉淀：每5条消息后静默执行 experience_curator

### 遇到的问题
| 问题 | 解决 |
|------|------|
| 用户终端写入文件全为0字节 | 改用write工具直接写入 |
| chats.py S4未接入 | 直接编辑恢复 |

### 验证
- "沉淀这个经验：Docker权限问题" → skill:experience_curator → 写入experiences表 ✅

---

## T19 O7: 工程优化

**状态**: ✅ 异步任务队列完成（PostgreSQL迁移暂缓）(2026-08-06)

### 优化目标
1. 异步任务队列：文档上传/索引不阻塞接口（已完成）
2. PostgreSQL迁移：暂缓（用户决定数据库先不变）
3. 测试补充/Token统计：待后续

### 详细步骤（异步化）

**1. knowledge_service.py 拆分**
1. `upload_document`：只保存文件+建记录（embedding_status=processing），立即返回
2. `process_document(doc_id, project_id)`：后台索引（解析→分块→嵌入→存ChromaDB）
   - 关键：必须新建 SessionLocal 会话（请求的session后台时已关闭）

**2. rag_service.py**
- embed_texts 保持同步requests（由后台线程执行，不阻塞事件循环）

**3. knowledge.py 接口**
1. upload 接口加 `BackgroundTasks` 参数
2. `background_tasks.add_task(process_document, doc.id, project_id)` 注册后台任务
3. 全局上传同样异步
4. 知识库影响分析也放后台（等索引完成后再分析）

### 遇到的问题
| 问题 | 解决 |
|------|------|
| 后台任务不能复用请求的db session | process_document 内部新建 SessionLocal |
| embed用asyncio.run会阻塞/报错 | 保持同步requests，放后台线程执行 |

### 验证
- 上传接口0秒返回（原来等待索引）✅
- 3秒后后台自动完成索引（processing→completed）✅
