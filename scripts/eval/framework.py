"""
统一评测框架 - Trace记录器
三层测试共用：
  ① 节点测试: 单节点直测，记录该节点耗时/token/输出
  ② 链路测试: 全链路，记录 coordinator→agent→tool 每步
  ③ 性能测试: 压测，记录延迟/token/并发

所有测试统一从 agent_executions 提取 Trace。
"""
import json
import time
import urllib.request
from typing import Optional

BASE = "http://localhost:8000/api/v1"


# ============ API 封装 ============
def api(method: str, path: str, body: dict = None, token: str = None, timeout: int = 180):
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


# ============ Trace 提取 ============
def get_executions(token: str, limit: int = 100) -> list:
    """获取最近Agent执行记录"""
    _, data = api("GET", f"/agents/executions?limit={limit}", None, token)
    return data or []


def capture_trace(token: str, before: list) -> list:
    """对比请求前后的executions，提取本次请求的trace"""
    after = get_executions(token)
    before_ids = {e["id"] for e in before}
    trace = [e for e in after if e["id"] not in before_ids]
    # 按时间排序（coordinator在前）
    return trace


def format_trace(trace: list) -> list:
    """把trace转为每步指标 dict"""
    steps = []
    for e in trace:
        tokens = e.get("tokens", {}) or {}
        steps.append({
            "agent": e.get("agent_type", "?"),
            "duration_ms": e.get("duration_ms"),
            "status": e.get("status", "?"),
            "prompt_tok": tokens.get("prompt_tokens", 0),
            "completion_tok": tokens.get("completion_tokens", 0),
            "total_tok": tokens.get("total_tokens", 0),
        })
    return steps


def trace_summary(steps: list) -> dict:
    """汇总trace指标"""
    total_ms = sum(s["duration_ms"] or 0 for s in steps)
    total_tok = sum(s["total_tok"] for s in steps)
    coordinator = next((s for s in steps if s["agent"] == "coordinator"), None)
    tools = [s for s in steps if "tool:" in s["agent"]]
    return {
        "steps_count": len(steps),
        "total_ms": total_ms,
        "total_tok": total_tok,
        "coordinator_ms": coordinator["duration_ms"] if coordinator else None,
        "coordinator_tok": coordinator["total_tok"] if coordinator else None,
        "tool_steps": len(tools),
        "tool_ms": sum(s["duration_ms"] or 0 for s in tools),
        "tool_tok": sum(s["total_tok"] for s in tools),
    }


# ============ 测试基座 ============
class EvalCase:
    """单个测试用例"""
    def __init__(self, name: str, case_type: str = "节点", desc: str = ""):
        self.name = name
        self.type = case_type  # 节点 / 链路 / 性能
        self.desc = desc

    def result(self, ok: bool, steps: list, extra: dict = None) -> dict:
        """生成标准用例结果"""
        r = {
            "case": self.name,
            "type": self.type,
            "ok": ok,
            "trace": steps,
            "summary": trace_summary(steps),
        }
        if extra:
            r.update(extra)
        return r


# ============ 环境准备 ============
def setup(prefix: str = "eval"):
    """注册测试用户+登录+建项目，返回 token/pid"""
    uname, email = f"{prefix}u", f"{prefix}@test.com"
    api("POST", "/auth/register", {"username": uname, "email": email, "password": "123456"})
    _, login = api("POST", "/auth/login", {"email": email, "password": "123456"})
    token = login["access_token"]
    _, proj = api("POST", "/projects", {"name": f"{prefix}项目"}, token)
    return token, proj["id"]


def new_chat(token: str, pid: str, title: str = "t"):
    """创建聊天，返回chat_id"""
    _, chat = api("POST", f"/projects/{pid}/chats", {"title": title}, token)
    return chat["id"]


def save_json(name: str, data: dict):
    """保存结果到 eval_results/"""
    import os
    os.makedirs("eval_results", exist_ok=True)
    with open(f"eval_results/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存: eval_results/{name}.json")
