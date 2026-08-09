"""
测试B: 真实链路并发（聊天含LLM）+ 延迟拆分
测: 5并发同时发聊天（每个都走coordinator+LLM+工具），测排队/超时/成功率
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/concurrency_test.py
"""
import sys, os, json, time, threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from framework import api, get_executions, capture_trace, format_trace, trace_summary, setup, new_chat, save_json


def main():
    token, pid = setup("conc")
    print("=" * 60)
    print("测试B: 真实链路并发（聊天含LLM）")
    print("=" * 60)

    # 5并发聊天（每个含LLM调用）
    ok, times, errors = 0, [], []
    lock = threading.Lock()

    def worker(i):
        nonlocal ok
        try:
            chat = new_chat(token, pid, f"cw{i}")
            t0 = time.time()
            st, resp = api("POST", f"/chats/{chat}/messages", {"content": f"介绍一下FastAPI的特点第{i}次"}, token, timeout=120)
            elapsed = time.time() - t0
            with lock:
                times.append(elapsed)
                if st == 200 and resp.get("content"):
                    ok += 1
                else:
                    errors.append((i, st, str(resp)[:60]))
        except Exception as e:
            with lock:
                errors.append((i, 0, str(e)[:60]))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    total = time.time() - t0

    times.sort()
    print(f"\n5并发聊天（含LLM）:")
    print(f"  成功率: {ok}/5")
    print(f"  总耗时: {total:.1f}s")
    print(f"  各耗时: {[round(t,1) for t in times]}")
    if times:
        print(f"  平均: {sum(times)/len(times):.1f}s | 最快: {times[0]:.1f}s | 最慢: {times[-1]:.1f}s")
    if errors:
        print(f"  错误: {errors[:3]}")
        # 检查是否排队（最后一个开始时间）
    print(f"  说明: {'✅ 并发正常，无超时' if ok==5 else '❌ 有失败'}")

    # 延迟拆分（单请求完整链路）
    print("\n" + "=" * 60)
    print("延迟拆分（单请求完整链路）")
    print("=" * 60)
    chat = new_chat(token, pid, "lat")
    before = get_executions(token)
    t0 = time.time()
    st, resp = api("POST", f"/chats/{chat}/messages", {"content": "沉淀这个经验：测试延迟拆分"}, token, timeout=120)
    api_total = time.time() - t0
    trace = format_trace(capture_trace(token, before))
    summary = trace_summary(trace)
    print(f"API总耗时: {api_total:.2f}s")
    for s in trace:
        print(f"  {s['agent']:<40} {s['duration_ms']}ms | {s['total_tok']}tok | {s['status']}")
    print(f"  Σ {summary['total_ms']}ms | {summary['total_tok']}tok")
    if trace:
        # 耗时占比
        total_ms = summary['total_ms']
        print(f"\n耗时占比:")
        for s in trace:
            pct = (s['duration_ms'] or 0) / total_ms * 100 if total_ms else 0
            print(f"  {s['agent']:<40} {pct:.0f}%")

    result = {
        "concurrency": {"ok": ok, "total": 5, "total_s": round(total, 2), "times": [round(t,1) for t in times], "errors": errors[:3]},
        "latency_split": {"api_total": round(api_total, 2), "trace": trace, "summary": summary},
    }
    save_json("concurrency_test", result)


if __name__ == "__main__":
    main()
