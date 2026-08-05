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


# ============ 记忆提取输出 ============
class MemoryItem(BaseModel):
    """单条记忆"""
    memory_type: Literal["decision", "progress", "problem", "preference"] = Field(
        description="记忆类型: decision=决策, progress=进度, problem=问题, preference=偏好"
    )
    content: str = Field(description="记忆内容，一句话概括")
    importance: int = Field(default=3, ge=1, le=5, description="重要度1-5")


class MemoriesExtractOutput(BaseModel):
    """从对话提取多条记忆"""
    memories: list[MemoryItem] = Field(default_factory=list, description="提取出的记忆列表")


# ============ 主动成长输出 ============
class LearningPlanItem(BaseModel):
    """单条学习计划"""
    category: str = Field(description="薄弱类别，如Redis")
    title: str = Field(description="学习计划标题")
    content: str = Field(description="学习计划内容（markdown，含学习步骤和建议）")


class LearningPlanOutput(BaseModel):
    """学习计划列表"""
    plans: list[LearningPlanItem] = Field(default_factory=list)


class DocUpdateCheckOutput(BaseModel):
    """文档更新检查"""
    should_update: bool = Field(description="是否需要更新文档")
    reason: str = Field(default="", description="更新原因和建议")


class KnowledgeImpactOutput(BaseModel):
    """知识库影响分析"""
    impact: bool = Field(description="是否影响已有方案")
    reason: str = Field(default="", description="影响分析说明")
