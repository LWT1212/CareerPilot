# CareerPilot 评测报告

> 关联方案: docs/EVALUATION-PLAN.md | 用例集: docs/TEST-CASES.md
> 开始: 2026-08-06

---

## 评测进度总览

| 评测项 | 状态 | 结果 |
|--------|------|------|
| 第0步 可观测性(token) | ✅ | usage记录到agent_executions |
| ★Coordinator节点 | ✅ | 96% |
| ★Experience节点 | ✅ | 100% |
| ★Interview节点 | ✅ | 通过 |
| ★Document节点 | ⚠️ | **发现content为空缺陷** |
| ★Knowledge节点 | ✅ | RAG命中+GitHub工具 |
| 层面2 Tool Calling | ⏳ | 待测 |
| 层面3 MCP | ⏳ | 待测 |
| 层面4 回答质量 | ⏳ | 待测 |
| 层面5 Memory | ⏳ | 待测 |
| 层面6 协作 | ⏳ | 待测 |
| 层面7 异常降级 | ⏳ | 待测 |
| 层面8 性能 | ⏳ | 待测 |
| 层面9 Redis | ⏳ | 待测 |

---

## Coordinator 节点评测（96%）

**结果文件**: scripts/eval/results/coordinator_eval.json

| 指标 | 值 |
|------|-----|
| Intent Routing Accuracy | 24/25 = 96.0% |
| 平均耗时 | 5.61s |
| 正向通过率 | 14/15 (93%) |
| 反向通过率 | 5/5 (100%) |
| 边界通过率 | 5/5 (100%) |

**误判案例**: "总结一下这个月的开发进度" → document（应 experience），置信度0.9

**失败用例明细**:
| 输入 | 期望 | 实际 | 置信度 | 类型 |
|------|------|------|--------|------|
| 总结一下这个月的开发进度 | experience | document | 0.90 | 正向 |

---

## Experience 节点评测（100%）

**结果文件**: scripts/eval/results/experience_eval.json

| 用例 | 结果 | 详情 |
|------|------|------|
| N3-01 保存经验 | ✅ | 14.1s，参数完整 |
| N3-01b DB写入+参数完整 | ✅ | type=bug, solution有值 |
| N3-02 查询经验 | ✅ | 7.1s，正确返回 |
| N3-05 无项目上下文 | ✅ | 0.0s，提示需要项目 |
| N3-06 无类型输入 | ✅ | 18.1s，自动推断type |

**关键验证**: 结构化提取的 type 字段正确（bug），solution 完整——T14 结构化输出生效。

---

## Interview 节点评测（通过）

| 用例 | 结果 | 详情 |
|------|------|------|
| N4-01 薄弱点识别 | ✅ | 10.5s，返回统计+薄弱点 |
| N4-02 学习计划生成 | ✅ | 1个Redis学习计划 |
| N4-04 无面试数据 | ✅ | 8.0s，返回空统计不崩溃 |

---

## Document 节点评测（⚠️ 发现缺陷）

| 用例 | 结果 | 详情 |
|------|------|------|
| N5-01 生成README | ✅ | 18.3s，"文档 readme 已保存 v1" |
| N5-01b 文档写入DB | ✅ | 1个文档 |
| N5-03 查询文档 | ❌ | **content为空（len=0）** |

### 🐛 发现的缺陷: Document Agent 保存空内容

**现象**: save_document 调用成功（v1），但文档 content 为空。

**根因分析**:
- Document Agent 的 `_agent_with_tools` 里，save_document 的 content 来自 `ToolCallOutput.arguments`
- LLM 只判断"需要调用 save_document"并给了 doc_type，但 **content 参数没生成**（或为空）
- 代码里没有"content 为空时先让 LLM 生成内容"的兜底

**影响**: 生成 README 等文档时，文档内容为空——功能缺陷

**修复建议**: save_document 调用前，若 content 为空，先用 LLM 生成文档内容再保存。

---

## Knowledge 节点评测（通过）

| 用例 | 结果 | 详情 |
|------|------|------|
| N2-01 RAG命中 | ✅ | 13.6s，回答含RDB+AOF（忠于文档）|
| N2-06 GitHub工具 | ✅ | 9.2s，返回fastapi真实数据 |

**关键验证**: RAG 检索正确命中知识库并基于文档回答（无幻觉）。

---

## 发现的缺陷汇总

| # | 缺陷 | 严重度 | 状态 |
|---|------|--------|------|
| 1 | Document Agent 保存文档 content 为空 | 高 | ✅ 已修复 |

### 缺陷1修复记录

**修复**: langgraph_workflow.py `_agent_with_tools` 中 save_document 分支加 content 兜底：
- content 为空或 <20字符时，先用 LLM 生成完整文档内容再保存

**验证**: 生成README后 content=3844字符（修复前为0）✅

---

## 下一步

- 修复 Document content 为空缺陷
- 继续: Tool Calling专项 / MCP / Memory / 降级 / 性能 / Redis

---

## Tool Calling 评测（层面2，88%）

**结果文件**: scripts/eval/results/tool_calling_eval.json

| 指标 | 值 |
|------|-----|
| Tool Selection Accuracy | 7/8 = 88% |
| 整体通过率 | 7/8 = 88% |

### 用例明细

| 用例 | 期望工具 | 实际 | 结果 |
|------|----------|------|------|
| 沉淀经验×2 | save_experience | skill/tool 路径 | ✅ |
| 看最近经验 | get_recent_experiences | experience(tool:get_recent_experiences) | ✅ |
| 面试统计 | get_interview_stats | interview(tool:get_interview_stats) | ✅ |
| 生成PRD | save_document | document(tool:save_document) | ✅ |
| 看README | get_document | knowledge(tool:search_project_knowledge) | ❌ |
| GitHub仓库 | github_repo_info | knowledge(tool:github_repo_info) | ✅ |
| Web搜索 | web_search | knowledge(tool:web_search) | ✅ |

### 步骤级指标（每次请求的trace）

| 步骤 | 平均耗时 | 平均token | 说明 |
|------|----------|-----------|------|
| coordinator | 0ms（Redis缓存命中）| 245tok | 意图识别缓存生效 |
| tool执行 | 3670ms | 245tok | 实际工具调用 |

### 🐛 发现的缺陷2: get_document 路由偏差

"看看项目有没有README" 被 Coordinator 识别为 knowledge（查知识库），而不是 document（查文档）。
- **影响**: 文档查询类请求可能走错 Agent
- **根因**: 意图识别对"查看文档"类请求与"查知识"区分不清
- **建议**: 优化意图识别提示词，区分"查知识库"vs"查项目文档"

### 🐛 发现的缺陷3: token 统计不完整

coordinator 的 token 显示 245（非0）但工具步骤也是245——每次都是同一个值，说明 `get_last_usage()` 记录的是"最后一次LLM调用"的usage，多步骤时可能被覆盖/重复。需按节点分别记录。

---

## 综合评测（层面3/5/6/8/9）

**结果文件**: scripts/eval/results/remaining_evals.json

| 层面 | 结果 | 详情 |
|------|------|------|
| 3 MCP | ✅ 100% | 10/10成功率，平均延迟0.82s |
| 5 Memory | ✅ | 5条决策记忆，跨会话召回PostgreSQL |
| 6 协作 | ✅ | Trace完整（coordinator→knowledge(tool)链）|
| 8 性能 | ✅ | 并发10读接口10/10成功，总耗时0.07s |
| 9 Redis | ❌ | 缓存命中未生效（缺陷4）|

### 🐛 缺陷4: Redis缓存key含聊天历史，导致无法命中

**现象**: 同一问题第1次9.1s，第2次5.36s（应0s），且回答不一致。

**根因**: chat_completion 缓存key = system_prompt + 用户消息 + **最近6条history**。
两次调用时，chat里第1轮的user+assistant消息已入库，导致第2次的history不同→key不同→未命中。

**影响**: 聊天场景缓存几乎失效（只有完全相同的context才能命中）。

**修复建议**: 缓存key只基于"用户消息+system_prompt"（不考虑history），或按聊天上下文单独设计。

### 🐛 缺陷5: Skill调用不记录到agent_executions

**现象**: 走 skill 路径的请求（如"沉淀经验"）不产生 trace 记录。

**根因**: chats.py 中 skill 命中时直接 skills_manager.execute，未调用 _record_execution。

**影响**: 可观测性缺口，skill 调用无法在 executions 中追踪。

**修复建议**: skill 路径也记录 agent_executions。
