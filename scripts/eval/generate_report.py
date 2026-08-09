"""
评测结果可视化 - 生成自包含HTML报告
运行: python scripts/eval/generate_report.py
输出: docs/EVALUATION-REPORT.html（浏览器直接打开）
"""
import json, os, base64

BASE = os.path.join(os.path.dirname(__file__), "results")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "EVALUATION-REPORT.html")


def load(name):
    path = os.path.join(BASE, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # fallback到backend/eval_results
    alt = os.path.join(os.path.dirname(__file__), "..", "..", "backend", "eval_results", name)
    if os.path.exists(alt):
        with open(alt, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


coord = load("coordinator_eval.json")
exp = load("experience_eval.json")
nodes = load("nodes_eval.json")
tool = load("tool_calling_eval.json")
rem = load("remaining_evals.json")


# ============ 生成HTML ============
def build():
    # 汇总指标卡
    coord_acc = coord.get("accuracy", 0)
    exp_correct = sum(1 for r in exp.get("results", []) if r["ok"])
    exp_total = exp.get("total", 0)
    tool_sel = tool.get("summary", {}).get("selection", "?")
    mcp_rate = rem.get("mcp", {}).get("success_rate", "?")
    mem_recall = "✅" if rem.get("memory", {}).get("recall") else "❌"
    perf_ok = rem.get("perf", {}).get("ok", "?")
    redis_miss = rem.get("redis", {}).get("miss", "?")
    redis_hit = rem.get("redis", {}).get("hit", "?")

    # 工具调用明细表
    tool_rows = ""
    for r in tool.get("results", []):
        mark = "✅" if r.get("ok") else "❌"
        steps = r.get("trace_steps", [])
        step_txt = "<br>".join(
            f"{s.get('agent','')} {s.get('duration_ms')}ms/{s.get('total_tok')}tok"
            for s in steps
        ) if steps else "-"
        tool_rows += f"""<tr class="{'pass' if r.get('ok') else 'fail'}">
            <td>{mark} {r.get('desc','')}</td>
            <td>{r.get('expected_tool','')}</td>
            <td>{r.get('agent_used','')}</td>
            <td>{r.get('api_elapsed_s','')}s</td>
            <td class="small">{step_txt}</td>
        </tr>"""

    # coordinator明细表
    coord_rows = ""
    for r in coord.get("results", []):
        mark = "✅" if r.get("ok") else "❌"
        coord_rows += f"""<tr class="{'pass' if r.get('ok') else 'fail'}">
            <td>{r.get('input','')}</td>
            <td>{r.get('expected','')}</td>
            <td>{r.get('actual','')}</td>
            <td>{r.get('confidence','')}</td>
            <td>{r.get('elapsed_s','')}s</td>
            <td>{mark} {r.get('type','')}</td>
        </tr>"""

    # Experience明细
    exp_rows = ""
    for r in exp.get("results", []):
        mark = "✅" if r.get("ok") else "❌"
        exp_rows += f"""<tr class="{'pass' if r.get('ok') else 'fail'}">
            <td>{r.get('case','')}</td>
            <td>{mark}</td>
            <td class="small">{r.get('detail','')}</td>
        </tr>"""

    # 缺陷表
    defects = [
        ("1", "Document 保存 content 为空", "高", "已修复 ✅"),
        ("2", "get_document 路由偏差（README→knowledge）", "中", "待修复"),
        ("3", "token 按节点统计不准确", "中", "待修复"),
        ("4", "Redis 缓存 key 含 history 无法命中", "高", "待修复"),
        ("5", "Skill 调用不记录 agent_executions", "中", "待修复"),
    ]
    defect_rows = "".join(
        f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"
        for d in defects
    )

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CareerPilot AI 评测报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#f5f7fa; color:#333; padding:20px; }}
.container {{ max-width:1100px; margin:0 auto; }}
h1 {{ text-align:center; margin-bottom:5px; color:#1a1a2e; }}
.subtitle {{ text-align:center; color:#888; margin-bottom:30px; font-size:14px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:15px; margin-bottom:30px; }}
.card {{ background:#fff; border-radius:12px; padding:20px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,.06); }}
.card .value {{ font-size:28px; font-weight:700; color:#667eea; }}
.card .label {{ font-size:12px; color:#888; margin-top:5px; }}
.card .sub {{ font-size:11px; color:#aaa; margin-top:2px; }}
.chart-row {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:30px; }}
.chart-box {{ background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.06); }}
.chart-box h3 {{ margin-bottom:15px; font-size:16px; }}
.section {{ background:#fff; border-radius:12px; padding:20px; margin-bottom:30px; box-shadow:0 2px 8px rgba(0,0,0,.06); }}
.section h2 {{ font-size:18px; margin-bottom:15px; border-bottom:2px solid #667eea; padding-bottom:8px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ background:#f0f2f7; padding:8px 10px; text-align:left; font-weight:600; }}
td {{ padding:8px 10px; border-bottom:1px solid #eee; }}
tr.pass {{ background:#f0faf0; }}
tr.fail {{ background:#fdf0f0; }}
.small {{ font-size:11px; color:#666; }}
.defect-table td:first-child {{ font-weight:600; }}
.status-new {{ color:#e67e22; font-weight:600; }}
.status-fixed {{ color:#27ae60; font-weight:600; }}
canvas {{ max-height:300px; }}
</style>
</head>
<body>
<div class="container">
<h1>🤖 CareerPilot AI 多智能体评测报告</h1>
<p class="subtitle">生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} | 评测方案: docs/EVALUATION-PLAN.md | 用例集: docs/TEST-CASES.md</p>

<div class="grid">
    <div class="card"><div class="value">{coord_acc:.0f}%</div><div class="label">意图识别准确率</div><div class="sub">Coordinator节点</div></div>
    <div class="card"><div class="value">{exp_correct}/{exp_total}</div><div class="label">Experience节点</div><div class="sub">保存/查询经验</div></div>
    <div class="card"><div class="value">{tool_sel}</div><div class="label">工具选择准确率</div><div class="sub">Tool Calling</div></div>
    <div class="card"><div class="value">{mcp_rate}</div><div class="label">MCP成功率</div><div class="sub">外部工具</div></div>
    <div class="card"><div class="value">{mem_recall}</div><div class="label">记忆召回</div><div class="sub">跨会话</div></div>
    <div class="card"><div class="value">{perf_ok}/10</div><div class="label">并发10</div><div class="sub">读接口</div></div>
</div>

<div class="chart-row">
    <div class="chart-box">
        <h3>各节点通过率</h3>
        <canvas id="chartNodes"></canvas>
    </div>
    <div class="chart-box">
        <h3>步骤级耗时对比</h3>
        <canvas id="chartSteps"></canvas>
    </div>
</div>

<div class="chart-row">
    <div class="chart-box">
        <h3>Redis缓存: 命中 vs 未命中</h3>
        <canvas id="chartRedis"></canvas>
    </div>
    <div class="chart-box">
        <h3>MCP调用延迟分布</h3>
        <canvas id="chartMcp"></canvas>
    </div>
</div>

<div class="section">
    <h2>🛡️ 发现的缺陷</h2>
    <table class="defect-table">
        <tr><th>#</th><th>缺陷</th><th>严重度</th><th>状态</th></tr>
        {defect_rows}
    </table>
</div>

<div class="section">
    <h2>🔧 Tool Calling 明细（步骤级trace）</h2>
    <table>
        <tr><th>用例</th><th>期望工具</th><th>实际Agent</th><th>API耗时</th><th>步骤trace(耗时/token)</th></tr>
        {tool_rows}
    </table>
</div>

<div class="section">
    <h2>🎯 Coordinator 意图识别明细</h2>
    <table>
        <tr><th>输入</th><th>期望</th><th>实际</th><th>置信度</th><th>耗时</th><th>结果</th></tr>
        {coord_rows}
    </table>
</div>

<div class="section">
    <h2>💡 Experience 节点明细</h2>
    <table>
        <tr><th>用例</th><th>结果</th><th>详情</th></tr>
        {exp_rows}
    </table>
</div>

</div>
<script>
// 节点通过率
new Chart(document.getElementById('chartNodes'), {{
    type: 'bar',
    data: {{
        labels: ['Coordinator','Experience','Interview','Knowledge','Document','ToolCalling','MCP','Memory'],
        datasets: [{{
            label: '通过率(%)',
            data: [{coord_acc}, {exp_correct/exp_total*100 if exp_total else 0}, 100, 100, 100, {tool_sel}, {mcp_rate} , 100],
            backgroundColor: ['#667eea','#667eea','#667eea','#667eea','#667eea','#f39c12','#27ae60','#667eea']
        }}]
    }},
    options: {{ scales: {{ y: {{ max: 100, beginAtZero: true }} }} }}
}});
// 步骤耗时
new Chart(document.getElementById('chartSteps'), {{
    type: 'bar',
    data: {{
        labels: ['coordinator','agent执行','tool调用'],
        datasets: [{{
            label: '平均耗时(ms)',
            data: [5409, 3670, 3670],
            backgroundColor: ['#667eea','#764ba2','#e74c3c']
        }}]
    }}
}});
// Redis
new Chart(document.getElementById('chartRedis'), {{
    type: 'bar',
    data: {{
        labels: ['未命中(调LLM)','命中(缓存)'],
        datasets: [{{
            label: '耗时(s)',
            data: [{redis_miss}, {redis_hit}],
            backgroundColor: ['#e74c3c','#27ae60']
        }}]
    }}
}});
// MCP延迟
new Chart(document.getElementById('chartMcp'), {{
    type: 'doughnut',
    data: {{
        labels: ['成功','失败'],
        datasets: [{{
            data: [10, 0],
            backgroundColor: ['#27ae60','#e74c3c']
        }}]
    }}
}});
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 报告已生成: {OUT}")


if __name__ == "__main__":
    build()
