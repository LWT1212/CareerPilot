"""
节点级评测 - Experience节点（保存/查询经验）+ Tool Calling
运行: cd backend && source ../.venv/bin/activate && python ../scripts/eval/experience_eval.py
"""
import sys, os, json, time, sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

# 直接用API测试（真实环境）
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
    """注册+登录+建项目"""
    api("POST", "/auth/register", {"username": "eval_user", "email": "eval@test.com", "password": "123456"})
    _, login = api("POST", "/auth/login", {"email": "eval@test.com", "password": "123456"})
    token = login["access_token"]
    _, proj = api("POST", "/projects", {"name": "评测项目"}, token)
    pid = proj["id"]
    _, chat = api("POST", f"/projects/{pid}/chats", {"title": "评测"}, token)
    return token, pid, chat["id"]


def main():
    token, pid, chat_id = setup()
    results = []

    # ============ 正向用例 ============
    print("=" * 70)
    print("Experience节点评测")
    print("=" * 70)

    # N3-01 保存经验（完整参数）
    t0 = time.time()
    status, resp = api("POST", f"/chats/{chat_id}/messages", {
        "content": "沉淀这个经验：MySQL连接超时，原因是连接池耗尽，解决方案是调大连接池大小并加索引"
    }, token)
    elapsed = time.time() - t0
    agent_used = resp.get("agent_used", "?")
    ok = status == 200 and "已保存" in resp.get("content", "")
    results.append({"case": "N3-01 保存经验", "ok": ok, "detail": f"agent={agent_used}, {resp.get('content','')[:60]}"})
    print(f"N3-01 保存经验: {'✅' if ok else '❌'} ({elapsed:.1f}s) {resp.get('content','')[:60]}")

    # 检查DB是否真实写入
    time.sleep(1)
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend", "careerpilot.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT title, type, solution FROM experiences ORDER BY created_at DESC LIMIT 3")
    db_rows = cur.fetchall()
    conn.close()
    print(f"DB写入验证: {len(db_rows)}条")
    for r in db_rows:
        print(f"  📝 {r[0]} | type={r[1]} | solution={'有' if r[2] else '无'}")
    type_ok = any(r[1] in ("bug", "solution", "note", "lesson") for r in db_rows)
    sol_ok = any(r[2] for r in db_rows)
    results.append({"case": "N3-01b DB写入+参数完整", "ok": type_ok and sol_ok, "detail": f"type字段={[r[1] for r in db_rows]}"})
    print(f"N3-01b DB写入+参数完整(type+solution): {'✅' if type_ok and sol_ok else '❌'}")

    # N3-02 查询经验
    t0 = time.time()
    status, resp = api("POST", f"/chats/{chat_id}/messages", {"content": "看下项目最近的经验"}, token)
    elapsed = time.time() - t0
    ok = status == 200 and len(resp.get("content", "")) > 0
    results.append({"case": "N3-02 查询经验", "ok": ok, "detail": resp.get("content", "")[:60]})
    print(f"N3-02 查询经验: {'✅' if ok else '❌'} ({elapsed:.1f}s) {resp.get('content','')[:60]}")

    # ============ 反向用例 ============
    # N3-05 无项目上下文（全局聊天）
    _, global_chat = api("POST", "/chats", {"title": "全局"}, token)
    t0 = time.time()
    status, resp = api("POST", f"/chats/{global_chat['id']}/messages", {
        "content": "沉淀这个经验：测试无项目场景"
    }, token)
    elapsed = time.time() - t0
    content = resp.get("content", "")
    ok = status == 200
    results.append({"case": "N3-05 无项目上下文", "ok": ok, "detail": content[:60]})
    print(f"N3-05 无项目上下文: {'✅不崩溃' if ok else '❌'} ({elapsed:.1f}s) {content[:60]}")

    # N3-06 只给内容不给类型
    t0 = time.time()
    status, resp = api("POST", f"/chats/{chat_id}/messages", {
        "content": "沉淀这个经验：接口返回500但没别的信息"
    }, token)
    elapsed = time.time() - t0
    ok = status == 200
    results.append({"case": "N3-06 无类型输入", "ok": ok, "detail": resp.get("content", "")[:60]})
    print(f"N3-06 无类型输入: {'✅' if ok else '❌'} ({elapsed:.1f}s) {resp.get('content','')[:60]}")

    # ============ 汇总 ============
    correct = sum(1 for r in results if r["ok"])
    total = len(results)
    print("-" * 70)
    print(f"Experience节点: {correct}/{total} 通过 ({correct/total*100:.0f}%)")

    os.makedirs("eval_results", exist_ok=True)
    with open("eval_results/experience_eval.json", "w", encoding="utf-8") as f:
        json.dump({"correct": correct, "total": total, "results": results}, f, ensure_ascii=False, indent=2)
    print("结果已保存: eval_results/experience_eval.json")


if __name__ == "__main__":
    main()
