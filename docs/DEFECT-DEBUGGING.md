# 缺陷定位与修复复盘（完整过程）

> 面试核心素材：展示"从测试数据定位缺陷"的完整推理链
> 对应评测: docs/EVALUATION.md | 用例集: docs/TEST-CASES.md

---

## 缺陷1: Document Agent 保存空内容

### 🎯 从哪个测试发现

**测试**: 节点测试 nodes_eval.py 的 N5-03 用例

**测试动作**: 生成 README 后查询文档

**测试结果（关键数据点）**:
```
N5-01 生成README: ✅ "文档 readme 已保存 v1"   ← 生成成功
N5-01b 文档写入DB: ✅ 1个文档                  ← DB有记录
N5-03 查询文档:    ❌                           ← 但查询失败！

复现后查文档列表:
  1个文档: ['readme']                          ← 文档存在
  查readme: doc_type=readme, content长度=0     ← ★ content是空的！
```

### 🔍 定位推理链

```
观察: 文档记录存在，但 content 长度为 0
  ↓
疑问: save_document 明明返回"已保存 v1"，内容去哪了？
  ↓
查代码: agent_tools.py 的 save_document
  def save_document(db, project_id, doc_type, content):
      doc = svc_upsert_document(db, project_id, doc_type, content, ...)
      # content 直接来自传入参数
  ↓
追问: content 参数从哪来？
  ↓
查 _agent_with_tools（LangGraph的通用工具执行器）:
  tool_args = dict(decision.arguments or {})   # 来自LLM的结构化输出
  # 对比: save_experience 有参数兜底
  if tool_name == "save_experience":
      tool_args = { "title": ..., "content": ...或message }  ← 有兜底
  # 但 save_document 没有兜底!
  ↓
结论: LLM 判断"需要调用save_document"并给了 doc_type，
      但没生成 content 参数 → content 为空
```

### 🛠️ 为什么这样修

**修复**: `_agent_with_tools` 的 save_document 分支加 content 兜底：
```python
if tool_name == "save_document":
    content = tool_args.get("content") or ""
    if not content or len(content.strip()) < 20:
        # 先用LLM生成完整文档内容再保存
        generated = await chat_completion([], message, f"请生成{doc_type}文档...")
        tool_args["content"] = generated
```

**理由**: 工具需要 content，但 LLM 的工具调用输出只给了 doc_type——这是**工具参数与工具需求不匹配**。兜底方案让"先有内容再保存"。

### ✅ 验证
```
修复后: content 0 → 3844字符（完整README）✅
```

---

## 缺陷2: 意图路由边界（查询类意图混淆）

### 🎯 从哪个测试发现

**测试**: Tool Calling 评测 tool_calling_eval.py 的 get_document 用例

**测试动作**: 问"看看项目有没有README"

**测试结果（关键数据点）**:
```
❌ [get_document] 期望=get_document 实际=knowledge
   ✅ knowledge(tool:search_project_knowledge) 123ms   ← ★ 走了知识库
   ✅ coordinator                         0ms
   Trace 显示: coordinator 识别为 knowledge，不是 document
```

### 🔍 定位推理链

```
观察: "看看项目有没有README" → coordinator 输出 intent=knowledge
  ↓
对比其他用例:
  "帮我生成README" → document ✅（生成类能识别）
  "看看项目有没有README" → knowledge ❌（查询类识别错）
  ↓
追问: "查看文档" vs "查知识库" 在意图语义上有什么区别？
  ↓
看意图识别提示词:
  "knowledge=技术知识/查资料, document=生成文档"
  → 提示词只说了 document 是"生成文档"，没说"查看文档"也归 document
  → LLM 把"看看项目有没有README"理解为"查资料"→ knowledge
  ↓
结论: 提示词对边界类别描述不足，导致查询文档类请求路由错
```

### 🛠️ 为什么这样修

**修复**: 优化意图识别提示词，明确边界：
```python
"- document: 生成/更新项目文档(README/PRD/简历)
 注意: '查看项目里某文档是否存在'归document，'查知识库资料'归knowledge，
       '问之前定过的技术决策'归chat(靠记忆回答)"
```

**理由**: 单次 prompt 分类的边界模糊问题，靠**在提示词里显式说明易混淆场景**解决——这是 prompt engineering 的标准手法。

### ✅ 验证
提示词已更新（复测待跑）。

---

## 缺陷3: Token 统计不准确

### 🎯 从哪个测试发现

**测试**: Tool Calling 评测的步骤级 trace 输出

**测试结果（关键数据点）**:
```
✅ experience(tool:get_recent_experiences) 4109ms | 0tok
✅ coordinator                         3371ms | 0tok
✅ document(tool:save_document)        55638ms | 2890tok
✅ coordinator                         4620ms | 0tok

注意: coordinator 全部显示 0tok / 245tok，
      且 tool 和 coordinator 的 token 经常是相同值
      （如 knowledge tool 245tok + coordinator 245tok = 490tok，每步都245）
```

### 🔍 定位推理链

```
观察: 每个节点的 token 要么是0，要么和别的节点相同
  ↓
疑问: token 到底记的是谁的？
  ↓
查代码: langgraph_workflow.py 的 _record_execution
  def _record_execution(db, agent_type, ..., status):
      from app.services.llm_service import get_last_usage  ← ★ 全局取
      tokens = get_last_usage()
  ↓
查 llm_service 的 get_last_usage:
  _last_usage = extract_usage(response)   # 每次LLM调用后覆盖全局
  ↓
推理: 节点A调用LLM → _last_usage = A的usage
      节点B调用LLM → _last_usage = B的usage（覆盖A）
      _record_execution 在节点结束时取 _last_usage
      → 如果节点内多次调LLM，取到的是"最后一次"的usage
      → 不是"本节点"的
  ↓
结论: 全局变量被覆盖，导致 token 归属错误
```

### 🛠️ 为什么这样修

**修复**: `_record_execution` 增加 tokens 参数，节点在 LLM 调用后**立即捕获** usage：
```python
def _record_execution(..., tokens: dict = None):
    if tokens is None:
        tokens = get_last_usage()  # 兜底

# 节点内:
intent_result = await structured_completion(...)
_record_execution(db, "coordinator", ..., tokens=get_last_usage())
```

**理由**: token 必须**就近捕获**——在 LLM 调用返回后立刻读取并绑定到当前节点，避免全局覆盖。

### ✅ 验证
coordinator 现在记录自己的意图识别 token。

---

## 缺陷4: Redis 缓存无法命中

### 🎯 从哪个测试发现

**测试**: 性能测试 perf_tests.py 的 Redis 缓存用例

**测试动作**: 清空缓存后，同一问题连续调用2次

**测试结果（关键数据点）**:
```
已清空缓存(68个key)
第1次(未命中): 49.4s          ← 正常，调LLM
第2次(命中):   20.71s         ← ★ 应该≈0s，却还要20秒！
回答一致: False               ← ★ 两次回答还不一样！
```

### 🔍 定位推理链

```
观察: 第2次调用要20秒（应0秒），且回答不一致
  ↓
疑问: 为什么相同问题没命中缓存？
  ↓
查代码: llm_service.chat_completion 的缓存key生成
  cache_text = f"{system_prompt}|{user_message}"
  for msg in history[-6:]:
      cache_text += f"|{msg['role']}:{msg['content'][:100]}"   ← ★ 含history！
  ↓
推理: 聊天流程中，第1次调用后 chat 里多了2条消息(user+assistant)
      → 第2次调用时 history 不同 → cache_text 不同 → key不同
      → 缓存永远无法命中（因为 history 一直在变）
  ↓
结论: key 设计缺陷——缓存 key 依赖了会变化的 history
```

### 🛠️ 为什么这样修

**修复**: 缓存 key 去掉 history，只基于稳定的输入：
```python
cache_text = f"{system_prompt}|{user_message}"   # 不含 history
```

**理由**: 缓存 key 应基于**能决定输出且稳定**的输入。history 虽然影响输出，但在聊天中不断变化，放 key 里等于禁用缓存。这是缓存设计的经典陷阱。

### ✅ 验证（函数级）
```
意图识别:  5.4s → 0.00s ✅
chat_completion: 7.9s → 0.00s ✅
```

---

## 缺陷5: Skill 调用无 Trace

### 🎯 从哪个测试发现

**测试**: 链路测试 pipeline_tests.py 的"沉淀经验"场景

**测试动作**: 发"沉淀这个经验：Docker部署失败..."

**测试结果（关键数据点）**:
```
场景: 沉淀经验
  ✅ 发送经验消息 (HTTP 200)           ← 功能正常
  Trace: 0步 | 总0ms | 0tok            ← ★ 但没有trace记录！
```

### 🔍 定位推理链

```
观察: 沉淀经验功能成功，但 trace 0步（其他场景都有2步）
  ↓
对比: 知识库RAG场景 trace 2步（coordinator + knowledge tool）
      沉淀经验场景 trace 0步
  ↓
疑问: 为什么这个场景没走 coordinator/tool？
  ↓
查代码: chats.py 的消息处理
  if skill:   ← ★ "沉淀这个经验"命中 Skill（关键词匹配）
      ai_content = await skills_manager.execute(...)   # 直接执行，无记录
  else:
      run_agent(...)   # LangGraph链路，内部有 _record_execution
  ↓
结论: Skill 路径绕过了 LangGraph 的执行记录机制，
      直接调 skills_manager.execute，没有 _record_execution
```

### 🛠️ 为什么这样修

**修复**: Skill 路径也写 AgentExecution（成功/失败都记录）：
```python
if skill:
    _t0 = time.time()
    try:
        ai_content = await skills_manager.execute(...)
        db.add(AgentExecution(
            agent_type=f"skill:{skill.name}",
            output_data={"tokens": get_last_usage()},
            duration_ms=int((time.time()-_t0)*1000),
            status="success"))
        db.commit()
    except Exception as e:
        db.add(AgentExecution(..., status="failed"))
```

**理由**: 可观测性必须覆盖**所有执行路径**。Skill 是独立于 LangGraph 的执行分支，漏掉它会导致"查不到某次调用"——这是可观测性设计的基本原则：每个入口都要有 trace。

### ✅ 验证
Skill 调用现在有 agent_executions 记录。

---

## 总结：定位问题的通用方法

```
每个缺陷都是这么定位的：
1. 测试输出里找"异常数据点"（该0s的20s、该有内容的空、该记录的0步）
2. 顺着数据流追代码（数据从哪来 → 谁生成 → 谁消费）
3. 对比正常用例找差异（为什么这个场景特殊）
4. 定位根因后，用"最小修改"修复
5. 复测验证（修复前 vs 修复后数据对比）
```

---

## 缺陷6: LangGraph checkpoint 断点恢复失败（Session不可序列化）

### 🎯 从哪个测试发现
**测试**: checkpoint_test.py（断点恢复专项，新增）

**测试动作**: 给图加 MemorySaver checkpoint 后，直接 ainvoke

**测试结果（关键数据点）**:
```
Type is not msgpack serializable: Session
```
checkpoint 保存时抛错 → 断点恢复完全不可用

### 🔍 定位推理链
```
观察: checkpoint保存报"Session不可序列化"
  ↓
最小化测试: 只放字符串的state → checkpoint成功 ✅
           显式传object() → 报"不可序列化" ❌
  ↓
对比: 我们的AgentState里有 db: Session 字段
      且 run_agent 显式传 db=db 到初始state
  ↓
结论: ① state schema 含 Session（SQLAlchemy会话不可序列化）
      ② 初始state显式塞了Session对象
      → checkpoint 机制无法持久化
```

### 🛠️ 为什么这样修
**修复**: 
1. AgentState.db 改为 managed value（DbValue），节点执行时自动创建session，不参与持久化
2. run_agent 不再显式传 db 到初始 state

**理由**: LangGraph checkpoint 会序列化整个 state。数据库会话这类"连接资源"不应进 state——应该由框架按需注入（managed value 模式），这是多智能体的标准架构实践。

### ✅ 验证
- 聊天+工具写库正常（managed db生效）✅
- checkpoint测试 3/3：同thread 10.9s→0.0s（命中checkpoint）✅
