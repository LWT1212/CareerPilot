# LLM 服务 - 统一封装 OpenAI 和 Ollama 双引擎
# 通过 config.py 的 LLM_PROVIDER 切换：openai 或 ollama

from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.config import settings


def get_llm() -> ChatOpenAI:
    """
    获取 LLM 实例（根据配置自动选择 OpenAI 或 Ollama）

    原理：
    - Ollama 提供 OpenAI 兼容接口（http://localhost:11434/v1）
    - 所以统一用 ChatOpenAI 客户端，只是 base_url 和 api_key 不同
    """
    if settings.LLM_PROVIDER == "ollama":
        # Ollama 的 OpenAI 兼容接口在 /v1 路径下
        return ChatOpenAI(
            model=settings.OLLAMA_MODEL,
            base_url=f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1",
            api_key="ollama",  # Ollama 不需要真实 key，填占位
            temperature=0.7,
        )
    else:
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )


def build_messages(history: list, user_message: str, system_prompt: str = "") -> list:
    """
    构建聊天消息列表

    history: 历史消息列表 [{"role": "user"/"assistant", "content": "..."}]
    user_message: 当前用户消息
    system_prompt: 系统提示词（可选，用来定义AI角色）
    """
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    for msg in history[-10:]:  # 只带最近10条，控制token
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=user_message))
    return messages


async def chat_completion(history: list, user_message: str, system_prompt: str = "") -> str:
    """
    一次性获取 LLM 回复（非流式）
    """
    llm = get_llm()
    messages = build_messages(history, user_message, system_prompt)
    response = await llm.ainvoke(messages)
    return response.content


async def stream_completion(history: list, user_message: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
    """
    流式获取 LLM 回复（SSE）
    逐字/逐token产出内容，前端实时显示
    """
    llm = get_llm()
    messages = build_messages(history, user_message, system_prompt)
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
