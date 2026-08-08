# CareerPilot 多智能体评测方案（v2）

> 状态: 待实施。先补可观测性（token+计时），再按8层面评测。
> 创建: 2026-08-06

## 第0步：补可观测性（评测数据基础）

现状缺失：
- token 用量（agent_executions 无 token 字段，messages.tokens_used 没写入）
- 阶段耗时拆分（coordinator/agent/tool/LLM 各段单独计时）
- 工具参数快照

补充实现：
| 补充项 | 实现 | 记录到哪 |
|--------|------|----------|
| token 用量 | LLM 响应取 usage | agent_executions.output_data.tokens + messages.tokens_used |
| 阶段耗时拆分 | 各节点单独计时 | agent_executions 增加字段 |
| 工具参数快照 | 记录完整 arguments | output_data.tool_args |

## 节点级评测（每个Agent节点单独测，核心）

> 不只测完整链路，每个节点单独直调，逐节点验证。

### 节点清单

| 节点 | 职责 | 工具 |
|------|------|------|
| coordinator | 意图识别/路由 | 无 |
| knowledge | 知识检索/外部查询 | search_project_knowledge / github_repo_info / web_search |
| experience | 经验管理 | save_experience / get_recent_experiences |
| interview | 面试分析 | get_interview_stats |
| document | 文档生成 | save_document / get_document |
| chat | 普通对话 | 无 |

### 统一评测矩阵（每个节点跑一遍）

| 维度 | 方法 | 指标 |
|------|------|------|
| 输入质量 | 各类测试输入（正常/边界/恶意） | 节点是否合理处理 |
| 输出正确性 | 期望输出 vs 实际输出 | Node Output Accuracy |
| 工具调用 | 该节点的工具是否正确选择/参数/执行 | Tool Selection / Success |
| State读写 | 节点是否正确读写 AgentState（intent/message/project_id） | State Correctness |
| 耗时 | 节点单独耗时（LLM+工具） | 平均耗时/P95 |
| token | 节点消耗 prompt/completion tokens | 平均token |
| 失败处理 | 注入错误（无项目/无知识库/LLM异常） | 降级成功率 |

### 各节点专项测试集

**N1 coordinator**（意图识别）
- 30问（5类各6）："分析面试失败"→interview、"生成README"→document 等
- 指标: Intent Accuracy / 置信度分布 / 低置信度兜底

**N2 knowledge**（知识检索）
- 有知识库: 问文档内问题→工具 search_project_knowledge→回答含文档要点
- 无知识库: 问技术问题→降级 web_search/github_repo_info 或直接回答
- 外部: "查GitHub fastapi"→github_repo_info
- 指标: RAG命中率 / 工具选择 / 回答正确性

**N3 experience**（经验管理）
- 记录: "记录经验:X，原因Y，解决Z"→save_experience→检查DB实际写入+参数完整(type字段)
- 查询: "看下最近经验"→get_recent_experiences
- 指标: 参数完整率 / 写入成功率 / type字段正确率

**N4 interview**（面试分析）
- 有数据: 添加弱题后问"薄弱点"→get_interview_stats→回答引用统计
- 无数据: 问"面试情况"→合理降级
- 指标: 统计注入率 / 建议质量

**N5 document**（文档生成）
- 生成: "生成README"→save_document→检查文档写入+版本递增
- 查询: "看下README"→get_document
- 指标: 生成质量 / 版本管理正确性

**N6 chat**（普通对话）
- 闲聊: 问候/天气→自然回答
- 记忆: 项目有记忆时→回答引用记忆
- 指标: 回答自然度 / 记忆注入

### 节点衔接（链路级）

5条链路 Coordinator→X，每条验证：
```
输入 → coordinator(intent=X) → X节点 → 工具 → 返回
```
- 链路完整率（每跳都有trace记录）
- 意图→节点一致性（coordinator识别的intent=实际进入的节点）

### 全链路 Trace 完整性

一次完整请求，agent_executions 应有：
```
coordinator(intent=interview, 400ms)
→ interview(1200ms)
→ interview(tool:get_interview_stats, 300ms)
```
- 指标: Trace Chain Completeness（每跳agent_type/duration/status齐全的比例）

## 层面1：Agent流程测试（编排）

- 测试集: 30问（5类各6个）
- 验证: intent正确 / 路由正确 / State传递
- 指标: Intent Routing Accuracy

## 层面2：Tool Calling测试（最重要）

- 测试集: 每工具3例（8个工具）
- 记录trace: agent/tool/arguments/status/duration
- 指标: Tool Selection Accuracy / 参数生成正确率 / Tool Execution Success Rate
- 核心: 通过trace看中间决策，不只看最终答案

## 层面3：MCP工具测试（外部能力）

- 单独测MCP不经过Agent: call_mcp_tool ×10
- 验证: 通信/JSON-RPC/返回结构/异常处理
- 指标: MCP成功率 / 平均延迟 / 降级生效

## 层面4：Agent回答质量测试（LLM输出）

- 正确性: RAG忠实度（上传已知文档→检查回答）
- 幻觉率: 问文档外问题→是否编造
- 完整性: 是否覆盖需求
- 测试集: 15问答对
- 指标: 准确性 / 幻觉率 / 完整性

## 层面5：Memory测试（长程）

- 第一轮告知项目信息→触发沉淀→第二轮提问
- 指标: Memory Recall Accuracy / Context Injection正确性

## 层面6：多Agent协作测试

- 职责边界: 各Agent只做自己事
- State统一: AgentState传递
- Trace追踪: 完整链 coordinator→agent→tool
- 指标: Trace完整率 / State传递正确率

## 层面7：异常和边界测试

- LLM异常/格式错误/超时
- 工具异常/参数异常
- MCP Server挂掉
- 指标: 降级成功率

## 层面8：性能测试

- 延迟拆分: 总耗时分解到Coordinator/Agent/Tool/MCP/LLM
- 并发: 100用户模拟
- Token统计: prompt/completion/total + 记忆注入+RAG上下文占比

## 层面9：Redis 缓存评测（T20新增）

**目标**：验证 LLM 响应缓存的实际收益（速度+token）

### 9.1 缓存命中 vs 未命中对比

```
同一问题连续调用2次（先清缓存再测）:

第1次(未命中): 响应时间 Xs, prompt_tokens A, completion_tokens B, total C
第2次(命中):   响应时间 ~0s, 消耗token 0

记录:
  未命中耗时 | 命中耗时 | 提速倍数
  未命中token | 命中token | token节省量
```

### 9.2 缓存命中率（真实场景）

- 用层面1-2的测试集跑2轮：第1轮全部未命中，第2轮应该全部命中
- 指标: `Cache Hit Rate` = 命中数 / 总请求数（第2轮应接近100%）

### 9.3 缓存正确性

- 同一问题两次回答是否一致（命中返回的内容=未命中内容）
- 不同 system_prompt 是否误命中（key含prompt，不应串）
- 不同历史上下文是否误命中

### 9.4 缓存降级

- 停掉 Redis → 聊天/意图识别是否正常（try-except降级，走LLM原逻辑）
- 指标: `Cache Failure Degradation`（Redis挂掉后成功率）

### 9.5 缓存空间/清理

- 测试后 keyspace: 缓存条目数、占内存（redis-cli dbsize / memory usage）

### 9.6 对多智能体链路的影响

- 完整聊天请求（含意图识别+工具判断）命中缓存后总耗时 vs 未命中
- 意图识别/工具判断这类结构化输出是否也受益于缓存

**指标汇总**：命中/未命中耗时对比、token节省、命中率、降级成功率

## 实施产物

- scripts/eval/node_eval.py (节点级评测：每个节点单独测+衔接链路) ★核心
- scripts/eval/orchestration_test.py (层面1)
- scripts/eval/tool_calling_test.py (层面2)
- scripts/eval/mcp_test.py (层面3)
- scripts/eval/output_quality_test.py (层面4)
- scripts/eval/memory_test.py (层面5)
- scripts/eval/collab_test.py (层面6)
- scripts/eval/fault_injection_test.py (层面7)
- scripts/eval/perf_test.py (层面8)
- scripts/eval/redis_cache_test.py (层面9，新增)
- docs/EVALUATION.md (汇总报告)

## 实施顺序

第0步 补可观测性 → ★节点级评测(核心) → 层面1-2 → 层面3+7 → 层面4-5 → 层面6+8 → 层面9(Redis) → 汇总报告

## 相关待办

- Redis 已实现（T20）：LLM响应缓存 ✅
- 会话缓存/热点数据缓存（V2后续可选）

