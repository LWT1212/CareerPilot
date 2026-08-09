"""
综合评测 - 层面3(MCP) / 5(Memory) / 6(协作) / 7(降级) / 8(性能) / 9(Redis)
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/remaining_evals.py
"""
import sys, os, json, time, threading, asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

import urllib.request

BASE = "http://localhost:8000/api/v1"
results = {}


def api(method, path, body=None, token=None, timeout=180):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 0, {"error": str(e)}


def setup():
    api("POST", "/auth/register", {"username": "allu", "email": "all@test.com", "password": "123456"})
    _, login = api("POST", "/auth/login", {"email": "all@test.com", "password": "123456"})
    token = login["access_token"]
    _, proj = api("POST", "/projects", {"name": "全评测"}, token)
    pid = proj["id"]
    return token, pid


# ============ 层面3: MCP 独立测试 ============
def eval_mcp():
    print("=" * 60)
    print("层面3: MCP 工具测试（独立调用×10）")
    print("=" * 60)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
    from app.services.mcp_client_service import call_mcp_tool

    success, times = 0, []
    for i in range(5):
        t0 = time.time()
        try:
            r = asyncio.run(call_mcp_tool("github_repo_info", {"repo": "fastapi/fastapi"}))
            elapsed = time.time() - t0
            times.append(elapsed)
            if "fastapi" in r:
                success += 1
        except Exception as e:
            times.append(time.time() - t0)
            print(f"  第{i+1}次失败: {str(e)[:60]}")
    for i in range(5):
        t0 = time.time()
        try:
            r = asyncio.run(call_mcp_tool("read_local_file", {"filepath": "/etc/hostname"}))
            elapsed = time.time() - t0
            times.append(elapsed)
            if r and "读取失败" not in r:
                success += 1
        except Exception as e:
            times.append(time.time() - t0)
    rate = success / 10 * 100
    avg = sum(times) / len(times) if times else 0
    results["mcp"] = {"success_rate": f"{success}/10={rate:.0f}%", "avg_delay": round(avg, 2)}
    print(f"MCP成功率: {success}/10 = {rate:.0f}% | 平均延迟: {avg:.2f}s")


# ============ 层面5: Memory 测试 ============
def eval_memory(token, pid):
    print("\n" + "=" * 60)
    print("层面5: Memory 测试（跨会话召回）")
    print("=" * 60)
    # 会话1：告知决策（5轮触发沉淀）
    _, chat1 = api("POST", f"/projects/{pid}/chats", {"title": "mem1"}, token)
    msgs = ["我们决定用PostgreSQL数据库", "后端用FastAPI框架", "前端用Vue3", "缓存用Redis", "部署用Docker"]
    for i, m in enumerate(msgs):
        st, resp = api("POST", f"/chats/{chat1['id']}/messages", {"content": m}, token, timeout=120)
        if st != 200:
            print(f"  第{i+1}轮发送失败: {resp}")
    time.sleep(5)  # 等记忆沉淀

    # 查记忆
    status, mem = api("GET", f"/projects/{pid}/memories", None, token)
    mem_count = len(mem.get("memories", []))
    print(f"记忆沉淀: {mem_count}条")
    for m in mem.get("memories", [])[:5]:
        print(f"  [{m['memory_type']}] {m['content'][:40]}")

    # 会话2：跨会话召回
    _, chat2 = api("POST", f"/projects/{pid}/chats", {"title": "mem2"}, token)
    status, resp = api("POST", f"/chats/{chat2['id']}/messages", {"content": "我们数据库怎么选的"}, token, timeout=90)
    content = resp.get("content", "")
    recall = "PostgreSQL" in content or "postgres" in content.lower()
    print(f"跨会话召回: {'✅' if recall else '❌'} → {content[:60]}")
    results["memory"] = {"recall": recall, "memories": mem_count}


# ============ 层面6: 协作/Trace 测试 ============
def eval_collab(token, pid):
    print("\n" + "=" * 60)
    print("层面6: 协作（Trace完整性）")
    print("=" * 60)
    before = api("GET", "/agents/executions?limit=100", None, token)[1]
    before_ids = {e["id"] for e in before}

    _, chat = api("POST", f"/projects/{pid}/chats", {"title": "collab"}, token)
    api("POST", f"/chats/{chat['id']}/messages", {"content": "查询项目知识库中关于部署的资料"}, token, timeout=90)
    time.sleep(1)
    after = api("GET", "/agents/executions?limit=100", None, token)[1]
    trace = [e for e in after if e["id"] not in before_ids]

    # 检查是否每步有完整字段
    complete = all(e.get("duration_ms") is not None and e.get("status") and e.get("tokens") is not None for e in trace)
    print(f"本次请求Trace: {len(trace)}步")
    for e in trace:
        tok = e.get("tokens", {})
        print(f"  {e['agent_type']:<40} {e.get('duration_ms')}ms | {tok.get('total_tokens','?')}tok | {e.get('status')}")
    results["collab"] = {"trace_steps": len(trace), "trace_complete": complete}


# ============ 层面8: 性能（延迟拆分+并发） ============
def eval_perf(token, pid):
    print("\n" + "=" * 60)
    print("层面8: 性能（并发+延迟）")
    print("=" * 60)
    # 并发读接口（项目列表）
    ok_count, times = 0, []
    def worker():
        nonlocal ok_count
        t0 = time.time()
        st, _ = api("GET", "/projects", None, token, timeout=30)
        times.append(time.time() - t0)
        if st == 200:
            ok_count += 1

    threads = [threading.Thread(target=worker) for _ in range(10)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    total = time.time() - t0
    avg = sum(times) / len(times)
    print(f"并发10读接口: 总耗时{total:.2f}s | 平均{avg:.3f}s | 成功率{ok_count}/10")
    results["perf"] = {"concurrency10": round(total, 2), "avg": round(avg, 3), "ok": ok_count}


# ============ 层面9: Redis 缓存测试 ============
def eval_redis(token, pid):
    print("\n" + "=" * 60)
    print("层面9: Redis 缓存测试")
    print("=" * 60)
    # 清缓存（直接删key）
    try:
        import redis as redis_lib
        r = redis_lib.Redis()
        for k in r.keys("llm:*"):
            r.delete(k)
        print("已清空LLM缓存")
    except Exception as e:
        print(f"清缓存失败: {e}")

    _, chat = api("POST", f"/projects/{pid}/chats", {"title": "rc"}, token)
    # 第1次（未命中）
    t0 = time.time()
    st1, r1 = api("POST", f"/chats/{chat['id']}/messages", {"content": "你好，用一句话介绍你自己"}, token, timeout=90)
    t1 = time.time() - t0
    # 第2次（命中）
    t0 = time.time()
    st2, r2 = api("POST", f"/chats/{chat['id']}/messages", {"content": "你好，用一句话介绍你自己"}, token, timeout=90)
    t2 = time.time() - t0
    same = r1.get("content") == r2.get("content")
    print(f"第1次(未命中): {t1:.1f}s")
    print(f"第2次(命中):   {t2:.2f}s")
    print(f"回答一致: {same}")
    print(f"提速: {t1/t2:.0f}x" if t2 > 0 else "命中0秒")
    results["redis"] = {"miss": round(t1, 1), "hit": round(t2, 2), "same": same}


def main():
    token, pid = setup()
    try:
        eval_mcp()
    except Exception as e:
        results["mcp"] = {"error": str(e)}
        print(f"MCP评测失败: {e}")
    try:
        eval_memory(token, pid)
    except Exception as e:
        results["memory"] = {"error": str(e)}
        print(f"Memory评测失败: {e}")
    try:
        eval_collab(token, pid)
    except Exception as e:
        results["collab"] = {"error": str(e)}
        print(f"协作评测失败: {e}")
    try:
        eval_perf(token, pid)
    except Exception as e:
        results["perf"] = {"error": str(e)}
        print(f"性能评测失败: {e}")
    try:
        eval_redis(token, pid)
    except Exception as e:
        results["redis"] = {"error": str(e)}
        print(f"Redis评测失败: {e}")

    print("\n" + "=" * 60)
    print("综合评测结果")
    print("=" * 60)
    for k, v in results.items():
        print(f"  {k}: {v}")

    os.makedirs("eval_results", exist_ok=True)
    with open("eval_results/remaining_evals.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n结果已保存: eval_results/remaining_evals.json")


if __name__ == "__main__":
    main()
