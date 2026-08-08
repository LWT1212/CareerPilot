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

## 实施产物

- scripts/eval/orchestration_test.py (层面1)
- scripts/eval/tool_calling_test.py (层面2)
- scripts/eval/mcp_test.py (层面3)
- scripts/eval/output_quality_test.py (层面4)
- scripts/eval/memory_test.py (层面5)
- scripts/eval/collab_test.py (层面6)
- scripts/eval/fault_injection_test.py (层面7)
- scripts/eval/perf_test.py (层面8)
- docs/EVALUATION.md (汇总报告)

## 实施顺序

第0步 补可观测性 → 层面1-2 → 层面3+7 → 层面4-5 → 层面6+8 → 汇总报告

## 相关待办

- Redis 未实现（V2规划）：缓存/会话存储，评测层面8并发测试可能需要
