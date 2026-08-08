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
        # OpenAI 兼容接口（支持 OpenAI 官方、阿里云DashScope等）
        # 有 OPENAI_BASE_URL 时用自定义地址，否则用 OpenAI 官方默认
        llm_kwargs = {
            "model": settings.OPENAI_MODEL,
            "api_key": settings.OPENAI_API_KEY,
            "temperature": 0.7,
        }
        if getattr(settings, "OPENAI_BASE_URL", ""):
            llm_kwargs["base_url"] = settings.OPENAI_BASE_URL
        return ChatOpenAI(**llm_kwargs)


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
    一次性获取 LLM 回复（非流式，带Redis缓存）
    相同请求命中缓存则直接返回，省token和时间
    """
    from app.services.redis_service import get_llm_cache, set_llm_cache

    # 生成缓存用的消息文本（含系统提示词，保证一致性）
    cache_text = f"{system_prompt}|{user_message}"
    for msg in history[-6:]:
        cache_text += f"|{msg['role']}:{msg['content'][:100]}"

    # 1. 查缓存
    cached = get_llm_cache(settings.LLM_PROVIDER, settings.OPENAI_MODEL or settings.OLLAMA_MODEL, cache_text)
    if cached:
        return cached

    # 2. 未命中 → 调LLM
    llm = get_llm()
    messages = build_messages(history, user_message, system_prompt)
    response = await llm.ainvoke(messages)

    # 3. 写缓存
    set_llm_cache(settings.LLM_PROVIDER, settings.OPENAI_MODEL or settings.OLLAMA_MODEL, cache_text, response.content)

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


async def structured_completion(schema_model, user_message: str,
                                system_prompt: str = "", max_retries: int = 1) -> object:
    """
    结构化输出：调用LLM并返回符合Pydantic schema的JSON

    性能优化：提示词用文字描述字段（不贴完整schema JSON），
    小模型生成量小、速度快、失败率低。
    """
    import json
    from pydantic import ValidationError

    # 生成简单的字段描述提示词（比贴完整schema更轻量）
    field_desc = _schema_field_description(schema_model)

    prompt = (
        f"{system_prompt}\n\n"
        f"只输出一个JSON对象，包含这些字段：{field_desc}\n"
        f"用户消息：{user_message}\n"
        f"直接输出JSON（不要输出其他文字）："
    )

    llm = get_llm()
    messages = build_messages([], prompt, "")

    # 结构化输出缓存（相同请求直接返回）
    from app.services.redis_service import get_llm_cache, set_llm_cache
    cache_key_text = f"struct|{schema_model.__name__}|{prompt}"
    cached = get_llm_cache(settings.LLM_PROVIDER, settings.OPENAI_MODEL or settings.OLLAMA_MODEL, cache_key_text)
    if cached:
        try:
            return schema_model(**json.loads(cached))
        except Exception:
            pass  # 缓存解析失败则重新生成

    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            text = response.content.strip()

            # 清理可能的markdown代码块
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            data = json.loads(text)
            # 写缓存
            set_llm_cache(settings.LLM_PROVIDER, settings.OPENAI_MODEL or settings.OLLAMA_MODEL, cache_key_text, text)
            return schema_model(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            if attempt == max_retries - 1:
                # 最后尝试：让模型直接输出原始JSON文本
                raise ValueError(f"结构化输出解析失败: {e}")

    raise ValueError("结构化输出失败")


def _schema_field_description(schema_model) -> str:
    """从Pydantic模型生成简洁的字段描述（支持嵌套模型+Literal枚举）"""
    import typing
    from pydantic import BaseModel

    def _describe(field) -> str:
        """生成单个字段描述"""
        annotation = field.annotation
        desc = field.description or ""

        # Literal 枚举：列出合法值
        if hasattr(annotation, "__origin__") and annotation.__origin__ is typing.Literal:
            values = annotation.__args__
            return f"(枚举:{'或'.join(str(v) for v in values)}) {desc}"

        # 嵌套 Pydantic 模型：递归生成子字段描述
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            sub = _schema_field_description(annotation)
            return f"(对象: {{{sub}}}) {desc}"

        # list[Model] 嵌套
        if hasattr(annotation, "__origin__") and annotation.__origin__ is list:
            args = annotation.__args__
            if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                sub = _schema_field_description(args[0])
                return f"(对象数组: [{{{sub}}}]) {desc}"

        # 普通类型
        if hasattr(annotation, "__name__"):
            return f"({annotation.__name__}) {desc}"
        return f"({annotation}) {desc}"

    fields = []
    for name, field in schema_model.model_fields.items():
        default = field.default
        if default is not None and default != "":
            fields.append(f"{name}{_describe(field)}, 默认{default}")
        else:
            fields.append(f"{name}{_describe(field)}")
    return "; ".join(fields)
