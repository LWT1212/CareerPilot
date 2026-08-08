"""
Redis 缓存服务 - LLM响应缓存/通用缓存
"""

import hashlib
import json

import redis

from app.config import settings

# Redis 客户端连接
_redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _make_key(prefix: str, content: str) -> str:
    """生成缓存key：前缀 + 内容hash"""
    content_hash = hashlib.md5(content.encode()).hexdigest()
    return f"{prefix}:{content_hash}"


# ============ LLM 响应缓存 ============

def get_llm_cache(provider: str, model: str, messages_text: str) -> str | None:
    """
    获取LLM响应缓存
    返回缓存的响应文本，未命中返回None
    """
    key = _make_key(f"llm:{provider}:{model}", messages_text)
    try:
        return _redis.get(key)
    except Exception as e:
        print(f"Redis读取失败: {e}")
        return None


def set_llm_cache(provider: str, model: str, messages_text: str, response: str) -> None:
    """写入LLM响应缓存"""
    key = _make_key(f"llm:{provider}:{model}", messages_text)
    try:
        _redis.set(key, response, ex=settings.LLM_CACHE_TTL)
    except Exception as e:
        print(f"Redis写入失败: {e}")


# ============ 通用缓存 ============

def get_cache(key: str) -> str | None:
    """通用缓存读取"""
    try:
        return _redis.get(key)
    except Exception as e:
        print(f"Redis读取失败: {e}")
        return None


def set_cache(key: str, value: str, ttl: int = 3600) -> None:
    """通用缓存写入"""
    try:
        _redis.set(key, value, ex=ttl)
    except Exception as e:
        print(f"Redis写入失败: {e}")


def ping() -> bool:
    """测试Redis连接"""
    try:
        return bool(_redis.ping())
    except Exception:
        return False
