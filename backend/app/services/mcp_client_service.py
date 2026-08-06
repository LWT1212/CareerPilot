"""
MCP 客户端服务
作用: CareerPilot 的 Agent 通过它调用外部 MCP 工具（GitHub查询/网页搜索/文件读取）
原理: 启动 mcp_server.py 子进程，通过 stdio 协议通信（JSON-RPC）
"""

import os
import sys
from mcp import ClientSession, StdioServerParameters, stdio_client


# MCP 服务器脚本路径（backend/mcp_server.py）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # backend/
MCP_SERVER_SCRIPT = os.path.join(BASE_DIR, "mcp_server.py")


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    调用 MCP 服务器上的工具
    - tool_name: 工具名 (github_repo_info / read_local_file / web_search)
    - arguments: 工具参数 dict

    流程:
    1. 启动 mcp_server.py 子进程 (stdio 管道)
    2. 建立 MCP 会话
    3. 调用工具
    4. 关闭连接
    """
    # 1. 配置子进程参数（用当前 Python 解释器运行 mcp_server.py）
    server_params = StdioServerParameters(
        command=sys.executable,  # 必须用当前解释器，确保导入mcp库
        args=[MCP_SERVER_SCRIPT],
        cwd=BASE_DIR,
    )

    # 2. 建立连接（async with 自动管理生命周期）
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化握手
            await session.initialize()
            # 调用工具
            result = await session.call_tool(tool_name, arguments)

            # 3. 解析返回结果（MCP返回的是content列表）
            if result.content:
                return str(result.content[0].text)
            return str(result)


# ============ 封装成异步工具（供Agent在事件循环中调用） ============

async def github_repo_info(repo: str, **kwargs) -> str:
    """查询GitHub仓库信息（MCP工具）"""
    return await call_mcp_tool("github_repo_info", {"repo": repo})


async def web_search(query: str, **kwargs) -> str:
    """网页搜索（MCP工具）"""
    return await call_mcp_tool("web_search", {"query": query})


async def read_local_file(filepath: str, **kwargs) -> str:
    """读取本地文件（MCP工具）"""
    return await call_mcp_tool("read_local_file", {"filepath": filepath})
