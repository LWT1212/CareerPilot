"""
链路测试 - 5个关键场景全链路（少量用例，验证编排）
每个场景: 全链路API调用 + 提取完整trace + 验证端到端正确
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/pipeline_tests.py
"""
import sys, os, json, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from framework import api, get_executions, capture_trace, format_trace, trace_summary, setup, new_chat, save_json


def run_scenario(token, pid, name, steps, timeout=180):
    """执行一个链路场景（多步API调用），返回结果"""
    print(f"\n{'='*60}\n场景: {name}\n{'='*60}")
    before = get_executions(token)
    result = {"case": name, "ok": True, "steps": [], "checks": []}

    for step in steps:
        # step: (描述, 方法, 路径, body)
        desc, method, path, body = step
        st, resp = api(method, path, body, token, timeout)
        ok_step = st == 200
        result["steps"].append({
            "desc": desc, "method": method, "path": path,
            "status": st, "ok": ok_step,
            "content": resp.get("content", "")[:80] if isinstance(resp, dict) else str(resp)[:80],
        })
        result["ok"] = result["ok"] and ok_step
        print(f"  {'✅' if ok_step else '❌'} {desc} (HTTP {st})")
        if not ok_step:
            print(f"     resp: {str(resp)[:100]}")

    # 提取本场景完整trace
    trace = capture_trace(token, before)
    steps_metrics = format_trace(trace)
    summary = trace_summary(steps_metrics)
    result["trace"] = steps_metrics
    result["trace_summary"] = summary

    print(f"  Trace: {len(steps_metrics)}步 | 总{summary['total_ms']}ms | {summary['total_tok']}tok")
    for s in steps_metrics:
        print(f"    {s['agent']:<40} {s['duration_ms']}ms | {s['total_tok']}tok | {s['status']}")
    return result


def main():
    token, pid = setup("pipe")
    results = []

    # ============ 场景1: 沉淀经验（经验链路） ============
    chat = new_chat(token, pid, "p1")
    r1 = run_scenario(token, pid, "沉淀经验", [
        ("发送经验消息", "POST", f"/chats/{chat}/messages", {"content": "沉淀这个经验：Docker部署失败，权限不足，解决是加入docker group"}),
    ])
    # 验证DB落盘
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend", "careerpilot.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT title, type, solution FROM experiences ORDER BY created_at DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    db_ok = row and row[1] in ("bug", "solution", "note", "lesson") and row[2]
    r1["checks"].append({"check": "DB落盘(type+solution)", "ok": db_ok, "detail": str(row)})
    r1["ok"] = r1["ok"] and db_ok
    print(f"  {'✅' if db_ok else '❌'} DB落盘验证: {row}")
    results.append(r1)

    # ============ 场景2: 知识库RAG（上传→问文档） ============
    boundary = "testboundary123"
    file_content = "Redis支持RDB快照和AOF日志两种持久化机制。RDB在指定时间间隔保存快照，AOF记录每次写操作。"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"redis.txt\"\r\n"
        f"Content-Type: text/plain\r\n\r\n{file_content}\r\n--{boundary}--\r\n"
    ).encode()
    import urllib.request
    req = urllib.request.Request(
        f"http://localhost:8000/api/v1/projects/{pid}/knowledge",
        data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        doc = json.loads(resp.read().decode())
    print(f"\n上传文档: {doc['filename']} ({doc['embedding_status']})")
    time.sleep(5)  # 等后台索引

    chat2 = new_chat(token, pid, "p2")
    r2 = run_scenario(token, pid, "知识库RAG", [
        ("问文档内问题", "POST", f"/chats/{chat2}/messages", {"content": "Redis有哪些持久化机制"}),
    ])
    content = r2["steps"][0].get("content", "")
    rag_ok = "RDB" in content and "AOF" in content
    r2["checks"].append({"check": "RAG命中(RDB+AOF)", "ok": rag_ok, "detail": content[:60]})
    r2["ok"] = r2["ok"] and rag_ok
    print(f"  {'✅' if rag_ok else '❌'} RAG命中验证")
    results.append(r2)

    # ============ 场景3: 面试弱题→学习计划（主动成长链路） ============
    before3 = get_executions(token)
    _, iv = api("POST", f"/projects/{pid}/interviews", {"company": "字节", "position": "后端"}, token)
    iv_id = iv["id"]
    for q, rating in [("Redis持久化", 2), ("Redis集群", 1), ("Redis缓存", 2)]:
        api("POST", f"/interviews/{iv_id}/questions", {"question": q, "category": "Redis", "rating": rating}, token)
    time.sleep(3)  # 等薄弱点分析
    status, plans = api("GET", f"/projects/{pid}/learning-plans", None, token)
    plan_ok = status == 200 and len(plans) > 0
    r3 = {
        "case": "面试弱题→学习计划", "ok": plan_ok,
        "steps": [{"desc": f"添加3个Redis弱题", "ok": True}],
        "checks": [{"check": "学习计划生成", "ok": plan_ok, "detail": f"{len(plans)}个"}],
        "trace": [], "trace_summary": {"total_ms": 0, "total_tok": 0},
    }
    print(f"\n{'✅' if plan_ok else '❌'} 场景: 面试弱题→学习计划 ({len(plans)}个计划)")
    results.append(r3)

    # ============ 场景4: 跨会话记忆（长期记忆链路） ============
    chat4 = new_chat(token, pid, "p4")
    for m in ["我们决定用PostgreSQL", "我们决定用FastAPI"]:
        api("POST", f"/chats/{chat4}/messages", {"content": m}, token, timeout=90)
    time.sleep(3)
    chat5 = new_chat(token, pid, "p5")
    before5 = get_executions(token)
    st, resp5 = api("POST", f"/chats/{chat5}/messages", {"content": "我们数据库怎么选的"}, token, timeout=90)
    content5 = resp5.get("content", "")
    recall_ok = "PostgreSQL" in content5 or "postgres" in content5.lower()
    trace5 = capture_trace(token, before5)
    r4 = {
        "case": "跨会话记忆", "ok": recall_ok,
        "steps": [{"desc": "会话1告知决策→会话2提问", "ok": True}],
        "checks": [{"check": "召回PostgreSQL", "ok": recall_ok, "detail": content5[:60]}],
        "trace": format_trace(trace5),
        "trace_summary": trace_summary(format_trace(trace5)),
    }
    print(f"\n{'✅' if recall_ok else '❌'} 场景: 跨会话记忆 → {content5[:50]}")
    results.append(r4)

    # ============ 场景5: MCP外部工具（GitHub链路） ============
    chat6 = new_chat(token, pid, "p6")
    before6 = get_executions(token)
    st, resp6 = api("POST", f"/chats/{chat6}/messages", {"content": "帮我查GitHub上fastapi/fastapi仓库"}, token, timeout=90)
    content6 = resp6.get("content", "")
    mcp_ok = "fastapi" in content6.lower() and ("star" in content6.lower() or "语言" in content6)
    trace6 = capture_trace(token, before6)
    r5 = {
        "case": "MCP外部工具", "ok": mcp_ok,
        "steps": [{"desc": "查GitHub仓库", "ok": st == 200}],
        "checks": [{"check": "返回仓库数据", "ok": mcp_ok, "detail": content6[:60]}],
        "trace": format_trace(trace6),
        "trace_summary": trace_summary(format_trace(trace6)),
    }
    print(f"\n{'✅' if mcp_ok else '❌'} 场景: MCP外部工具")
    results.append(r5)

    # ============ 汇总 ============
    print("\n" + "=" * 60)
    print("链路测试汇总")
    print("=" * 60)
    ok_count = sum(1 for r in results if r["ok"])
    for r in results:
        print(f"  {'✅' if r['ok'] else '❌'} {r['case']}: {r['trace_summary'].get('total_ms','-')}ms | {r['trace_summary'].get('total_tok','-')}tok")
    print(f"链路测试通过: {ok_count}/{len(results)}")

    save_json("pipeline_tests", {
        "ok": ok_count, "total": len(results),
        "rate": f"{ok_count}/{len(results)}",
        "results": results,
    })


if __name__ == "__main__":
    main()
