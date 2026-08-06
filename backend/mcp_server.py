"""
CareerPilot MCP 服务器
提供外部工具给 AI Agent 调用：GitHub查询/文件读取/网页搜索
"""
import json
import urllib.request


def _fetch_json(url: str) -> dict:
    """发送GET请求并解析JSON"""
    req = urllib.request.Request(url, headers={"User-Agent": "CareerPilot"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _fetch_text(url: str) -> str:
    """发送GET请求获取文本"""
    req = urllib.request.Request(url, headers={"User-Agent": "CareerPilot"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode(errors="ignore")


# ============ MCP 服务器 ============
from mcp.server.mcpserver import MCPServer

# 创建 MCP 服务器
mcp = MCPServer("CareerPilot Tools")


# ============ 工具1: GitHub仓库查询 ============
@mcp.tool()
def github_repo_info(repo: str) -> str:
    """
    查询GitHub仓库的详细信息。
    参数repo格式: 用户名/仓库名，如 LWT1212/CareerPilot
    返回: 仓库描述、star数、语言、最近更新时间等
    """
    try:
        data = _fetch_json(f"https://api.github.com/repos/{repo}")
        return json.dumps({
            "name": data.get("full_name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count"),
            "language": data.get("language"),
            "forks": data.get("forks_count"),
            "updated_at": data.get("updated_at"),
            "license": (data.get("license") or {}).get("name"),
            "url": data.get("html_url"),
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"查询失败: {e}（请确认仓库名格式为 用户名/仓库名）"


# ============ 工具2: 读取本地文件 ============
@mcp.tool()
def read_local_file(filepath: str) -> str:
    """
    读取本地文本文件的内容。
    参数filepath: 文件路径，如 backend/app/main.py
    返回: 文件前3000字符
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content[:3000] + ("...(已截断)" if len(content) > 3000 else "")
    except Exception as e:
        return f"读取失败: {e}"


# ============ 工具3: 网页搜索 ============
@mcp.tool()
def web_search(query: str) -> str:
    """
    网页搜索。
    参数query: 搜索关键词
    返回: 前5条搜索结果（标题+链接+摘要）
    """
    try:
        import urllib.parse
        import re

        # 使用DuckDuckGo的HTML搜索结果（免费，无需API key）
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        html = _fetch_text(url)

        # 解析搜索结果
        results = []
        # 匹配结果块
        for m in re.finditer(
            r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>',
            html
        )[:5]:
            link = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2))
            results.append({"title": title, "url": link})

        if not results:
            return "没有找到搜索结果"
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"搜索失败: {e}"


# ============ 启动 ============
if __name__ == "__main__":
    mcp.run(transport="stdio")
