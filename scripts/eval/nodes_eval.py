"""
节点级评测 - Interview节点 + Document节点 + Knowledge节点
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/nodes_eval.py
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
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def setup():
    api("POST", "/auth/register", {"username": "eval2", "email": "eval2@test.com", "password": "123456"})
    _, login = api("POST", "/auth/login", {"email": "eval2@test.com", "password": "123456"})
    token = login["access_token"]
    _, proj = api("POST", "/projects", {"name": "评测2"}, token)
    pid = proj["id"]
    return token, pid


def main():
    token, pid = setup()
    results = []
    print("=" * 70)
    print("Interview/Document/Knowledge节点评测")
    print("=" * 70)

    # ============ Interview ============
    print("\n--- Interview节点 ---")
    # 准备数据：创建面试+弱题
    _, iv = api("POST", f"/projects/{pid}/interviews", {
        "company": "字节跳动", "position": "后端", "result": "offer"
    }, token)
    iv_id = iv["id"]
    for q, rating in [("Redis持久化机制", 2), ("Redis集群部署", 1), ("Redis缓存穿透", 2)]:
        api("POST", f"/interviews/{iv_id}/questions", {
            "question": q, "category": "Redis", "rating": rating
        }, token)

    time.sleep(2)  # 等AI薄弱点分析

    # N4-01 问薄弱点
    _, chat = api("POST", f"/projects/{pid}/chats", {"title": "iv"}, token)
    t0 = time.time()
    status, resp = api("POST", f"/chats/{chat['id']}/messages", {"content": "我们的面试薄弱点是什么"}, token)
    elapsed = time.time() - t0
    content = resp.get("content", "")
    ok = status == 200 and ("Redis" in content or "薄弱" in content)
    results.append({"case": "N4-01 薄弱点识别", "ok": ok, "detail": content[:80]})
    print(f"N4-01 薄弱点识别: {'✅' if ok else '❌'} ({elapsed:.1f}s) {content[:80]}")

    # N4-02 学习计划API
    t0 = time.time()
    status, plans = api("GET", f"/projects/{pid}/learning-plans", None, token)
    elapsed = time.time() - t0
    ok = status == 200 and len(plans) > 0
    results.append({"case": "N4-02 学习计划生成", "ok": ok, "detail": f"{len(plans)}个计划"})
    print(f"N4-02 学习计划生成: {'✅' if ok else '❌'} ({elapsed:.1f}s) {len(plans)}个")

    # N4-04 无面试数据项目
    _, pid2_proj = api("POST", "/projects", {"name": "空项目"}, token)
    pid2 = pid2_proj["id"]
    _, chat2 = api("POST", f"/projects/{pid2}/chats", {"title": "empty"}, token)
    t0 = time.time()
    status, resp = api("POST", f"/chats/{chat2['id']}/messages", {"content": "我的面试情况怎么样"}, token)
    elapsed = time.time() - t0
    content = resp.get("content", "")
    ok = status == 200
    results.append({"case": "N4-04 无面试数据", "ok": ok, "detail": content[:60]})
    print(f"N4-04 无面试数据: {'✅不崩溃' if ok else '❌'} ({elapsed:.1f}s) {content[:60]}")

    # ============ Document ============
    print("\n--- Document节点 ---")
    _, dchat = api("POST", f"/projects/{pid}/chats", {"title": "doc"}, token)
    t0 = time.time()
    status, resp = api("POST", f"/chats/{dchat['id']}/messages", {"content": "帮我生成README文档"}, token)
    elapsed = time.time() - t0
    content = resp.get("content", "")
    ok = status == 200 and ("README" in content or "已保存" in content or "已创建" in content)
    results.append({"case": "N5-01 生成文档", "ok": ok, "detail": content[:60]})
    print(f"N5-01 生成README: {'✅' if ok else '❌'} ({elapsed:.1f}s) {content[:60]}")

    # 检查文档是否写入
    time.sleep(1)
    status, docs = api("GET", f"/projects/{pid}/documents", None, token)
    ok = status == 200 and any(d.get("doc_type") == "readme" for d in docs)
    results.append({"case": "N5-01b 文档写入", "ok": ok, "detail": f"{len(docs)}个文档"})
    print(f"N5-01b 文档写入DB: {'✅' if ok else '❌'}")

    # N5-03 查看文档
    t0 = time.time()
    status, doc = api("GET", f"/projects/{pid}/documents/readme", None, token)
    elapsed = time.time() - t0
    ok = status == 200 and doc.get("content")
    results.append({"case": "N5-03 查询文档", "ok": ok, "detail": doc.get("content", "")[:40]})
    print(f"N5-03 查询文档: {'✅' if ok else '❌'} ({elapsed:.1f}s)")

    # ============ Knowledge ============
    print("\n--- Knowledge节点 ---")
    # 上传文档
    import io, uuid
    boundary = uuid.uuid4().hex
    file_content = "Redis支持RDB快照和AOF日志两种持久化机制。RDB在指定时间间隔保存快照，AOF记录每次写操作。"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="redis.txt"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
        f"{file_content}\r\n"
        f"--{boundary}--\r\n"
    ).encode()
    req = urllib.request.Request(
        f"{BASE}/projects/{pid}/knowledge",
        data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                 "Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        doc = json.loads(resp.read().decode())
    print(f"上传文档: {doc['filename']} (状态={doc['embedding_status']})")

    # 等索引完成
    time.sleep(5)

    # N2-01 RAG检索（问文档内问题）
    _, kchat = api("POST", f"/projects/{pid}/chats", {"title": "knowledge"}, token)
    t0 = time.time()
    status, resp = api("POST", f"/chats/{kchat['id']}/messages", {"content": "Redis有哪些持久化机制"}, token)
    elapsed = time.time() - t0
    content = resp.get("content", "")
    ok = status == 200 and ("RDB" in content and "AOF" in content)
    results.append({"case": "N2-01 RAG命中", "ok": ok, "detail": content[:80]})
    print(f"N2-01 RAG命中(RDB+AOF): {'✅' if ok else '❌'} ({elapsed:.1f}s) {content[:80]}")

    # N2-06 外部GitHub工具
    t0 = time.time()
    status, resp = api("POST", f"/chats/{kchat['id']}/messages", {"content": "帮我查GitHub上fastapi/fastapi仓库信息"}, token)
    elapsed = time.time() - t0
    content = resp.get("content", "")
    ok = status == 200 and ("fastapi" in content.lower() and ("star" in content.lower() or "语言" in content))
    results.append({"case": "N2-06 GitHub工具", "ok": ok, "detail": content[:80]})
    print(f"N2-06 GitHub工具调用: {'✅' if ok else '❌'} ({elapsed:.1f}s) {content[:80]}")

    # ============ 汇总 ============
    correct = sum(1 for r in results if r["ok"])
    total = len(results)
    print("-" * 70)
    print(f"节点评测汇总: {correct}/{total} 通过 ({correct/total*100:.0f}%)")
    for r in results:
        print(f"  {'✅' if r['ok'] else '❌'} {r['case']}: {r['detail'][:50]}")

    os.makedirs("eval_results", exist_ok=True)
    with open("eval_results/nodes_eval.json", "w", encoding="utf-8") as f:
        json.dump({"correct": correct, "total": total, "results": results}, f, ensure_ascii=False, indent=2)
    print("结果已保存: eval_results/nodes_eval.json")


if __name__ == "__main__":
    main()
