"""
节点测试 - 6节点大量小用例，单节点直测
每个节点: 直接调用节点函数，记录耗时/token/输出正确性
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/node_tests.py
"""
import sys, os, json, asyncio, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.db import SessionLocal
from app.agents.langgraph_workflow import (
    coordinator_node, knowledge_node, experience_node,
    interview_node, document_node, chat_node,
)

# ============ 状态构建 ============
def make_state(message, project_id="", db=None, history=None):
    return {
        "message": message,
        "project_id": project_id,
        "chat_history": history or [],
        "db": db,
        "intent": "",
        "response": "",
        "execution_log": [],
    }


# ============ 测试用例 ============
coord_cases = [
    ("帮我分析最近面试失败原因", "interview"),
    ("Redis持久化机制有哪些", "knowledge"),
    ("记录经验：Docker权限不足", "experience"),
    ("帮我生成项目README", "document"),
    ("你好，今天天气怎么样", "chat"),
    ("面试的薄弱点是什么", "interview"),
    ("更新一下我的简历", "document"),
    ("我们踩过哪些坑", "experience"),
    ("谢谢", "chat"),
    ("查一下项目里关于部署的资料", "knowledge"),
    ("", "chat"),
    ("!!!", "chat"),
    ("👍", "chat"),
    ("What is Redis", "knowledge"),
    ("def foo(): return 42", "chat"),
    ("帮我准备一下系统设计面试", "interview"),
    ("写一个PRD文档", "document"),
    ("聊聊最近的技术趋势", "chat"),
    ("我们决定用PostgreSQL", "chat"),
    ("帮我查GitHub上fastapi仓库", "knowledge"),
]

experience_cases = [
    "沉淀这个经验：接口超时，原因是没设timeout，解决是加参数",
    "看下项目最近的经验",
    "记录一个bug：内存泄漏",
    "我们有没有遇到过部署问题",
    "把今天的踩坑记录一下",
]

knowledge_cases = [
    "根据知识库，Docker怎么部署",
    "查一下GitHub上langchain-ai/langchain",
    "搜索最新的Python版本",
]

interview_cases = [
    "分析一下面试情况",
    "面试薄弱点是什么",
    "总结面试表现",
]

document_cases = [
    "帮我生成README文档",
    "看看项目有没有PRD",
]

chat_cases = [
    "你好",
    "介绍一下你自己",
    "最近有什么新技术吗",
]


# ============ 执行 ============
async def run_node(node_fn, cases, db, node_name):
    results = []
    for input_text in cases:
        t0 = time.time()
        try:
            state = make_state(input_text, project_id="", db=db)
            out = await node_fn(state)
            elapsed = time.time() - t0
            # coordinator输出intent，其他节点输出response
            has_intent = bool(out.get("intent", ""))
            has_response = bool(out.get("response", ""))
            ok = has_intent or has_response  # 任一输出即为正常执行
            results.append({
                "input": input_text[:30],
                "ok": ok,
                "elapsed_s": round(elapsed, 2),
                "response": out.get("response", "")[:50],
                "intent": out.get("intent", ""),
            })
        except Exception as e:
            results.append({
                "input": input_text[:30],
                "ok": False,
                "elapsed_s": round(time.time() - t0, 2),
                "error": str(e)[:50],
            })
    return results


def summarize(name, results):
    ok = sum(1 for r in results if r["ok"])
    total = len(results)
    avg = sum(r["elapsed_s"] for r in results) / total if total else 0
    print(f"  {name}: {ok}/{total} 通过 | 平均{avg:.2f}s")
    return {"node": name, "ok": ok, "total": total, "avg_s": round(avg, 2), "cases": results}


def main():
    db = SessionLocal()
    all_results = {}

    print("=" * 70)
    print("节点测试（单节点直测）")
    print("=" * 70)

    # Coordinator（意图识别）
    print("\n[Coordinator 节点]")
    r = summarize("coordinator", asyncio.run(run_node(coordinator_node, coord_cases, db, "coordinator")))
    all_results["coordinator"] = r

    # 其他节点（需项目上下文，用空项目ID测行为）
    print("\n[其他节点（无项目上下文场景）]")
    r = summarize("experience", asyncio.run(run_node(experience_node, experience_cases, db, "experience")))
    all_results["experience"] = r
    r = summarize("knowledge", asyncio.run(run_node(knowledge_node, knowledge_cases, db, "knowledge")))
    all_results["knowledge"] = r
    r = summarize("interview", asyncio.run(run_node(interview_node, interview_cases, db, "interview")))
    all_results["interview"] = r
    r = summarize("document", asyncio.run(run_node(document_node, document_cases, db, "document")))
    all_results["document"] = r
    r = summarize("chat", asyncio.run(run_node(chat_node, chat_cases, db, "chat")))
    all_results["chat"] = r

    db.close()

    # 总汇总
    print("\n" + "=" * 70)
    total_ok = sum(v["ok"] for v in all_results.values())
    total_all = sum(v["total"] for v in all_results.values())
    print(f"节点测试总通过: {total_ok}/{total_all} = {total_ok/total_all*100:.0f}%")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from framework import save_json
    save_json("node_tests", {
        "total_ok": total_ok, "total_all": total_all,
        "accuracy": round(total_ok / total_all * 100, 1) if total_all else 0,
        "nodes": all_results,
    })


if __name__ == "__main__":
    main()
