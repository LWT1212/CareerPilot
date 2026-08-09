"""
Tool Calling 专项评测（层面2）- 步骤级指标
每个用例提取执行 trace：coordinator/agent/tool 各步耗时+token
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/tool_calling_eval.py
"""
import sys, os, json, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

import urllib.request

BASE = "http://localhost:8000/api/v1"


def api(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def setup():
    api("POST", "/auth/register", {"username": "toolu2", "email": "tool2@test.com", "password": "123456"})
    _, login = api("POST", "/auth/login", {"email": "tool2@test.com", "password": "123456"})
    token = login["access_token"]
    _, proj = api("POST", "/projects", {"name": "Tool评测2"}, token)
    pid = proj["id"]
    return token, pid


def get_executions(token, limit=50):
    """获取最近Agent执行记录（含每步耗时+token）"""
    _, data = api("GET", "/agents/executions?limit=" + str(limit), None, token)
    return data


def main():
    token, pid = setup()
    results = []

    test_cases = [
        ("save_experience", "沉淀这个经验：API接口超时，原因是未设置超时时间，解决是加timeout参数", "save_experience"),
        ("save_experience", "记录经验：内存泄漏，解决是及时释放连接", "save_experience"),
        ("get_recent_experiences", "看下我们项目最近的开发经验", "get_recent_experiences"),
        ("get_interview_stats", "统计一下项目的面试情况", "get_interview_stats"),
        ("save_document", "帮我生成一个PRD文档", "save_document"),
        ("get_document", "看看项目有没有README", "get_document"),
        ("github_repo_info", "查一下GitHub上langchain-ai/langchain这个仓库", "github_repo_info"),
        ("web_search", "搜索一下2026年最流行的Python框架", "web_search"),
    ]

    print("=" * 90)
    print("Tool Calling 评测（步骤级指标：每步耗时+token）")
    print("=" * 90)

    all_traces = []  # 收集所有trace做汇总

    for desc, input_text, expected_tool in test_cases:
        # 记录请求前的executions数量（用于过滤本次请求的trace）
        before = get_executions(token)
        before_count = len(before)

        _, chat = api("POST", f"/projects/{pid}/chats", {"title": desc}, token)
        t0 = time.time()
        status, resp = api("POST", f"/chats/{chat['id']}/messages", {"content": input_text}, token)
        total_elapsed = time.time() - t0
        agent_used = resp.get("agent_used", "?")
        content = resp.get("content", "")

        # 提取本次请求的trace（新增的executions）
        after = get_executions(token, limit=100)
        trace = [e for e in after if e["id"] not in {b["id"] for b in before}]

        # 解析每步
        steps = []
        for e in trace:
            tokens = e.get("tokens", {}) or {}
            steps.append({
                "agent": e["agent_type"],
                "duration_ms": e.get("duration_ms"),
                "status": e.get("status"),
                "prompt_tok": tokens.get("prompt_tokens", 0),
                "completion_tok": tokens.get("completion_tokens", 0),
                "total_tok": tokens.get("total_tokens", 0),
            })

        # 判断结果
        tool_called = expected_tool in agent_used or expected_tool in content
        success = status == 200 and len(content) > 0 and not content.startswith("（处理失败")
        ok = tool_called and success

        # 汇总本用例指标
        total_tok = sum(s["total_tok"] for s in steps)
        total_ms = sum(s["duration_ms"] or 0 for s in steps)
        coordinator_step = next((s for s in steps if s["agent"] == "coordinator"), None)
        agent_step = next((s for s in steps if "tool:" in s["agent"] or s["agent"] == desc), None)

        case_result = {
            "desc": desc,
            "input": input_text[:25],
            "expected_tool": expected_tool,
            "agent_used": agent_used,
            "tool_called": tool_called,
            "exec_success": success,
            "ok": ok,
            "api_elapsed_s": round(total_elapsed, 1),
            "trace_steps": steps,
            "steps_metrics": {
                "coordinator": coordinator_step,
                "agent": agent_step,
            },
            "sum_metrics": {"total_ms": total_ms, "total_tok": total_tok},
            "response": content[:50],
        }
        results.append(case_result)
        all_traces.extend(steps)

        # 打印步骤级明细
        print(f"\n{'✅' if ok else '❌'} [{desc}] 期望={expected_tool} 实际={agent_used} (API耗时{total_elapsed:.1f}s)")
        for s in steps:
            mark = "✅" if s["status"] == "success" else "❌"
            print(f"   {mark} {s['agent']:<35} {s['duration_ms']}ms | {s['total_tok']}tok")
        print(f"   Σ {len(steps)}步 | {total_ms}ms | {total_tok}tok")

    # ============ 汇总 ============
    print("\n" + "=" * 90)
    print("汇总指标")
    print("=" * 90)

    # 工具选择准确率
    tool_cases = [r for r in results if r.get("expected_tool")]
    sel_ok = sum(1 for r in tool_cases if r["tool_called"])
    print(f"Tool Selection Accuracy: {sel_ok}/{len(tool_cases)} = {sel_ok/len(tool_cases)*100:.0f}%")

    # 整体通过率
    ok_count = sum(1 for r in results if r["ok"])
    print(f"整体通过率: {ok_count}/{len(results)} = {ok_count/len(results)*100:.0f}%")

    # 各步骤平均耗时/token
    print("\n各步骤平均指标:")
    step_types = {}
    for s in all_traces:
        agent = "tool" if "tool:" in s["agent"] else s["agent"]
        step_types.setdefault(agent, []).append(s)
    for agent, ss in step_types.items():
        avg_ms = sum(s["duration_ms"] or 0 for s in ss) / len(ss)
        avg_tok = sum(s["total_tok"] for s in ss) / len(ss)
        print(f"  {agent:<30} 平均{avg_ms:.0f}ms | {avg_tok:.0f}tok | {len(ss)}次")

    # 耗时占比（找瓶颈）
    print("\n耗时占比（总耗时中每步占多少）:")
    total_ms_all = sum(s["duration_ms"] or 0 for s in all_traces)
    for agent, ss in step_types.items():
        agent_ms = sum(s["duration_ms"] or 0 for s in ss)
        pct = agent_ms / total_ms_all * 100 if total_ms_all else 0
        print(f"  {agent:<30} {agent_ms}ms ({pct:.0f}%)")

    # token占比
    total_tok_all = sum(s["total_tok"] for s in all_traces)
    print("\ntoken占比:")
    for agent, ss in step_types.items():
        agent_tok = sum(s["total_tok"] for s in ss)
        pct = agent_tok / total_tok_all * 100 if total_tok_all else 0
        print(f"  {agent:<30} {agent_tok}tok ({pct:.0f}%)")

    os.makedirs("eval_results", exist_ok=True)
    with open("eval_results/tool_calling_eval.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "summary": {
            "selection": f"{sel_ok}/{len(tool_cases)}",
            "overall": f"{ok_count}/{len(results)}",
        }}, f, ensure_ascii=False, indent=2)
    print("\n结果已保存: eval_results/tool_calling_eval.json")


if __name__ == "__main__":
    main()
