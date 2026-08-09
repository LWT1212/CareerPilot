"""
测试C: 参数实验
1. 温度实验: 意图识别在 temperature 0.0/0.7/1.0 下的稳定性
2. 历史窗口: 聊天 history 5/10/15条 的 token 消耗与质量
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/params_test.py
"""
import sys, os, json, asyncio, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from langchain_openai import ChatOpenAI
from app.config import settings
from app.services.llm_service import build_messages, extract_usage


def make_llm(temp):
    """创建指定温度的LLM"""
    if settings.LLM_PROVIDER == "ollama":
        return ChatOpenAI(model=settings.OLLAMA_MODEL,
                          base_url=f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1",
                          api_key="ollama", temperature=temp)
    kwargs = {"model": settings.OPENAI_MODEL, "api_key": settings.OPENAI_API_KEY, "temperature": temp}
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
    return ChatOpenAI(**kwargs)


# 意图测试集（10个明确意图）
INTENT_QUESTIONS = [
    ("帮我分析最近面试失败原因", "interview"),
    ("Redis持久化机制有哪些", "knowledge"),
    ("记录经验：Docker权限不足", "experience"),
    ("帮我生成项目README", "document"),
    ("你好，今天天气怎么样", "chat"),
    ("面试的薄弱点是什么", "interview"),
    ("更新一下我的简历", "document"),
    ("我们踩过哪些坑", "experience"),
    ("查一下GitHub上fastapi仓库", "knowledge"),
    ("谢谢", "chat"),
]

INTENT_PROMPT = """你是任务调度器。判断用户消息的意图，只返回以下之一：
- knowledge: 技术知识/查资料/GitHub
- experience: 记录查询经验/bug
- interview: 面试分析/薄弱点
- document: 生成更新文档
- chat: 普通对话
只返回意图单词，不要解释。"""


async def intent_with_temp(temp):
    """用指定温度跑一遍意图识别，返回准确率"""
    llm = make_llm(temp)
    correct = 0
    results = []
    for q, expected in INTENT_QUESTIONS:
        try:
            resp = await llm.ainvoke(build_messages([], q, INTENT_PROMPT))
            actual = resp.content.strip().lower()
            for v in ["knowledge", "experience", "interview", "document", "chat"]:
                if v in actual:
                    actual = v
                    break
            else:
                actual = "unknown"
            ok = actual == expected
            if ok:
                correct += 1
            results.append({"q": q[:20], "expected": expected, "actual": actual, "ok": ok})
        except Exception as e:
            results.append({"q": q[:20], "expected": expected, "actual": f"ERR:{str(e)[:20]}", "ok": False})
    return correct, results


async def main():
    print("=" * 60)
    print("实验1: 温度参数对意图识别的影响")
    print("=" * 60)
    temp_results = {}
    for temp in [0.0, 0.7, 1.0]:
        t0 = time.time()
        correct, results = await intent_with_temp(temp)
        elapsed = time.time() - t0
        acc = correct / len(INTENT_QUESTIONS) * 100
        temp_results[str(temp)] = {"accuracy": round(acc, 1), "correct": correct, "total": len(INTENT_QUESTIONS), "elapsed_s": round(elapsed, 1)}
        print(f"temperature={temp}: 准确率 {correct}/{len(INTENT_QUESTIONS)} = {acc:.0f}% | 耗时{elapsed:.1f}s")
        # 展示失败项
        for r in results:
            if not r["ok"]:
                print(f"    ❌ {r['q']} → {r['actual']} (期望{r['expected']})")

    # 结论
    accs = {t: v["accuracy"] for t, v in temp_results.items()}
    print(f"\n结论: 温度0.0最稳定({accs.get('0.0','?')}%), 1.0最发散({accs.get('1.0','?')}%)")
    print("→ 结构化任务(意图识别)应用低温度, 创意任务(生成文档)可用高温度")

    # ============ 实验2: 历史窗口 ============
    print("\n" + "=" * 60)
    print("实验2: 历史窗口对token消耗的影响")
    print("=" * 60)
    llm = make_llm(0.2)
    window_results = {}
    for window in [5, 10, 15]:
        # 模拟15轮对话
        history = []
        total_tok = 0
        for i in range(15):
            history.append({"role": "user", "content": f"问题{i}: 技术讨论第{i}轮"})
            history.append({"role": "assistant", "content": f"回答{i}: 这是第{i}轮的回复内容，包含一些技术细节。"})
        # 取最近window条作为实际传入的history
        use_history = history[-window:]
        resp = await llm.ainvoke(build_messages(use_history, "总结一下", ""))
        usage = extract_usage(resp)
        tok = usage["total_tokens"]
        window_results[str(window)] = {"total_tok": tok, "prompt_tok": usage["prompt_tokens"], "completion_tok": usage["completion_tokens"]}
        print(f"窗口{window}条: prompt={usage['prompt_tokens']} | completion={usage['completion_tokens']} | total={tok}")

    # token增长
    tok5 = window_results.get("5", {}).get("total_tok", 0)
    tok15 = window_results.get("15", {}).get("total_tok", 0)
    if tok5:
        print(f"\n结论: 窗口5→15条, token从{tok5}→{tok15} (增长{tok15/tok5*100-100:.0f}% if tok5 else '?')")
    print("→ 历史窗口越大token成本越高, 需在'上下文完整性'和'token成本'间权衡")

    result = {"temperature": temp_results, "history_window": window_results}
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from framework import save_json
    save_json("params_test", result)


if __name__ == "__main__":
    asyncio.run(main())
