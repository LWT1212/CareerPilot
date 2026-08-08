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
| 1 | Document Agent 保存文档 content 为空 | 高 | 待修复 |

---

## 下一步

- 修复 Document content 为空缺陷
- 继续: Tool Calling专项 / MCP / Memory / 降级 / 性能 / Redis
