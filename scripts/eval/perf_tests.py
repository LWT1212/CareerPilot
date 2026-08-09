"""
性能测试 - 单独压测
1. 延迟拆分（coordinator/agent/tool各段）
2. 并发压测（读接口/写接口）
3. token统计
4. Redis缓存命中/未命中
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/perf_tests.py
"""
import sys, os, json, time, threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from framework import api, get_executions, capture_trace, format_trace, trace_summary, setup, new_chat, save_json


# ============ 1. 延迟拆分 ============
def latency_split(token, pid):
    print("=" * 60)
    print("1. 延迟拆分（完整聊天请求的各段耗时）")
    print("=" * 60)
    chat = new_chat(token, pid, "perf")
    before = get_executions(token)
    t0 = time.time()
    st, resp = api("POST", f"/chats/{chat}/messages", {"content": "沉淀这个经验：连接池配置问题"}, token, timeout=120)
    api_total = time.time() - t0
    trace = format_trace(capture_trace(token, before))
    summary = trace_summary(trace)
    print(f"API总耗时: {api_total:.2f}s")
    for s in trace:
        print(f"  {s['agent']:<40} {s['duration_ms']}ms | {s['total_tok']}tok")
    print(f"  Σ {summary['total_ms']}ms | {summary['total_tok']}tok")
    return {"api_total": round(api_total, 2), "trace": trace, "summary": summary}


# ============ 2. 并发压测 ============
def concurrency(token, pid):
    print("\n" + "=" * 60)
    print("2. 并发压测")
    print("=" * 60)

    # 读接口并发
    ok_read, times_read = 0, []
    lock = threading.Lock()
    def read_worker():
        nonlocal ok_read
        t0 = time.time()
        st, _ = api("GET", "/projects", None, token, timeout=30)
        with lock:
            times_read.append(time.time() - t0)
            if st == 200:
                ok_read += 1
    threads = [threading.Thread(target=read_worker) for _ in range(20)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    read_total = time.time() - t0
    read_avg = sum(times_read) / len(times_read)
    print(f"读接口并发20: {ok_read}/20 成功 | 总{read_total:.2f}s | 平均{read_avg:.3f}s")

    # 写接口并发（聊天消息，会调LLM较慢，用5并发）
    ok_write = 0
    def write_worker():
        nonlocal ok_write
        chat = new_chat(token, pid, "cw")
        st, _ = api("POST", f"/chats/{chat}/messages", {"content": "你好"}, token, timeout=90)
        with lock:
            if st == 200:
                ok_write += 1
    threads = [threading.Thread(target=write_worker) for _ in range(5)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    write_total = time.time() - t0
    print(f"写接口并发5(调LLM): {ok_write}/5 成功 | 总{write_total:.2f}s")
    return {"read20": {"ok": ok_read, "total_s": round(read_total, 2), "avg_ms": round(read_avg*1000)}, "write5": {"ok": ok_write, "total_s": round(write_total, 2)}}


# ============ 3. token统计 ============
def token_stats(token, pid):
    print("\n" + "=" * 60)
    print("3. Token 统计")
    print("=" * 60)
    chat = new_chat(token, pid, "tok")
    before = get_executions(token)
    api("POST", f"/chats/{chat}/messages", {"content": "介绍一下你自己"}, token, timeout=90)
    trace = format_trace(capture_trace(token, before))
    total_tok = sum(s["total_tok"] for s in trace)
    print(f"本次请求: {len(trace)}步 | 总{total_tok}tok")
    for s in trace:
        print(f"  {s['agent']:<40} prompt={s['prompt_tok']} | completion={s['completion_tok']} | total={s['total_tok']}")
    return {"steps": len(trace), "total_tok": total_tok}


# ============ 4. Redis缓存 ============
def redis_test(token, pid):
    print("\n" + "=" * 60)
    print("4. Redis 缓存（命中 vs 未命中）")
    print("=" * 60)
    # 清缓存
    try:
        import redis as rl
        r = rl.Redis()
        n = len(r.keys("llm:*"))
        for k in r.keys("llm:*"):
            r.delete(k)
        print(f"已清空缓存({n}个key)")
    except Exception as e:
        print(f"清缓存失败: {e}")

    chat = new_chat(token, pid, "rc")
    # 用不同system_prompt的意图识别测（避免聊天历史干扰）
    t0 = time.time()
    st1, _ = api("POST", f"/chats/{chat}/messages", {"content": "用一句话介绍FastAPI"}, token, timeout=90)
    miss = time.time() - t0
    t0 = time.time()
    st2, _ = api("POST", f"/chats/{chat}/messages", {"content": "用一句话介绍FastAPI"}, token, timeout=90)
    hit = time.time() - t0
    print(f"未命中: {miss:.1f}s | 命中: {hit:.2f}s | 提速{miss/hit:.0f}x" if hit > 0 else "未命中0")
    return {"miss": round(miss, 1), "hit": round(hit, 2)}


def main():
    token, pid = setup("perf")
    results = {}
    results["latency"] = latency_split(token, pid)
    results["concurrency"] = concurrency(token, pid)
    results["token"] = token_stats(token, pid)
    results["redis"] = redis_test(token, pid)
    print("\n" + "=" * 60)
    print("性能测试汇总")
    print("=" * 60)
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    save_json("perf_tests", results)


if __name__ == "__main__":
    main()
