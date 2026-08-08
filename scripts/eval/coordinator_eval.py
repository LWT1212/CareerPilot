"""
节点级评测 - Coordinator意图识别 + 路由（层面1）
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/coordinator_eval.py
"""
import sys, os, json, asyncio, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.services.llm_service import structured_completion
from app.agents.agent_schemas import IntentOutput


# ============ 测试集（N1.1正向 + N1.2反向 + N1.3边界） ============
TEST_CASES = [
    # (输入, 期望intent, 类型)
    # --- 正向 ---
    ("帮我分析最近面试失败原因", "interview", "正向"),
    ("Redis持久化机制有哪些", "knowledge", "正向"),
    ("记录经验：Docker权限不足", "experience", "正向"),
    ("帮我生成项目README", "document", "正向"),
    ("你好，今天天气怎么样", "chat", "正向"),
    ("查一下项目里关于部署的资料", "knowledge", "正向"),
    ("面试的薄弱点是什么", "interview", "正向"),
    ("更新一下我的简历", "document", "正向"),
    ("我们踩过哪些坑", "experience", "正向"),
    ("谢谢", "chat", "正向"),
    ("如何用docker部署FastAPI", "knowledge", "正向"),
    ("总结一下这个月的开发进度", "experience", "正向"),
    ("帮我准备一下系统设计面试", "interview", "正向"),
    ("写一个PRD文档", "document", "正向"),
    ("聊聊最近的技术趋势", "chat", "正向"),
    # --- 反向（歧义/混合/空） ---
    ("", "chat", "反向-空输入"),
    ("!!!", "chat", "反向-符号"),
    ("帮我分析面试中Redis答得不好", "interview", "反向-混合意图"),
    ("生成README顺便记录个bug", "document", "反向-多意图"),
    ("asdfghjklqwertyuiop", "chat", "反向-乱码"),
    # --- 边界 ---
    ("好", "chat", "边界-单字"),
    ("What is Redis and how it works", "knowledge", "边界-英文"),
    ("def foo(): return 42", "chat", "边界-代码"),
    ("👍", "chat", "边界-表情"),
    ("详细解释一下分布式系统中的一致性协议包括Raft和Paxos以及ZAB的具体实现细节和优缺点比较", "knowledge", "边界-超长"),
]


async def main():
    results = []
    correct = 0

    for input_text, expected, case_type in TEST_CASES:
        start = time.time()
        try:
            intent_result = await structured_completion(
                IntentOutput,
                input_text,
                "判断用户消息的意图：knowledge=技术知识/查资料, experience=记录查询经验, interview=面试分析, document=生成文档, chat=普通对话。project_related=是否涉及项目内数据。"
            )
            actual = intent_result.intent
            confidence = intent_result.confidence
            elapsed = time.time() - start
            ok = (actual == expected)
            if ok:
                correct += 1
            results.append({
                "input": input_text[:40],
                "expected": expected,
                "actual": actual,
                "confidence": round(confidence, 2),
                "ok": ok,
                "type": case_type,
                "elapsed_s": round(elapsed, 2),
            })
        except Exception as e:
            results.append({
                "input": input_text[:40],
                "expected": expected,
                "actual": f"ERROR:{str(e)[:30]}",
                "confidence": 0,
                "ok": False,
                "type": case_type,
                "elapsed_s": round(time.time() - start, 2),
            })

    total = len(TEST_CASES)
    accuracy = correct / total * 100

    # 输出
    print("=" * 80)
    print(f"Coordinator 意图识别评测结果")
    print("=" * 80)
    print(f"{'输入':<40} {'期望':<12} {'实际':<12} {'置信':<6} {'耗时':<6} {'结果'}")
    print("-" * 80)
    for r in results:
        mark = "✅" if r["ok"] else "❌"
        print(f"{r['input']:<40} {r['expected']:<12} {r['actual']:<12} {r['confidence']:<6} {r['elapsed_s']:<6} {mark} ({r['type']})")

    print("-" * 80)
    print(f"Intent Routing Accuracy: {correct}/{total} = {accuracy:.1f}%")
    print(f"平均耗时: {sum(r['elapsed_s'] for r in results)/total:.2f}s")

    # 按类型统计
    print("\n按用例类型统计:")
    for t in ["正向", "反向", "边界"]:
        subset = [r for r in results if t in r["type"]]
        if subset:
            ok = sum(1 for r in subset if r["ok"])
            print(f"  {t}: {ok}/{len(subset)} ({ok/len(subset)*100:.0f}%)")

    # 保存结果
    os.makedirs("eval_results", exist_ok=True)
    with open("eval_results/coordinator_eval.json", "w", encoding="utf-8") as f:
        json.dump({"accuracy": accuracy, "total": total, "correct": correct, "results": results}, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: eval_results/coordinator_eval.json")


if __name__ == "__main__":
    asyncio.run(main())
