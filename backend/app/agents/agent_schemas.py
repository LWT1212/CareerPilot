# Agent结构化输出Schema
# 强制LLM输出固定JSON格式，避免文本解析不稳定

from pydantic import BaseModel, Field
from typing import Literal, Optional


# ============ 意图识别输出 ============
class IntentOutput(BaseModel):
    """意图识别结果"""
    intent: Literal["knowledge", "experience", "interview", "document", "chat"] = Field(
        description="用户消息意图分类"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="置信度0-1")
    project_related: bool = Field(default=False, description="是否与项目数据相关")


# ============ 工具调用输出 ============
class ToolCallOutput(BaseModel):
    """工具调用决策"""
    use_tool: bool = Field(description="是否调用工具")
    tool: Optional[str] = Field(default=None, description="工具名")
    arguments: dict = Field(default_factory=dict, description="工具参数")


# ============ 对话摘要输出 ============
class SummaryOutput(BaseModel):
    """对话摘要"""
    summary: str = Field(description="对话摘要，200字以内")


# ============ 经验结构化输出 ============
class ExperienceExtractOutput(BaseModel):
    """从用户描述中提取经验结构"""
    title: str = Field(description="经验标题")
    exp_type: Literal["bug", "solution", "architecture", "lesson", "note"] = Field(
        default="note", description="经验类型"
    )
    content: str = Field(description="问题/经验内容")
    solution: Optional[str] = Field(default=None, description="解决方案")
