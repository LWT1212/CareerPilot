# LangGraph 多智能体工作流
# 架构: Coordinator(意图识别) → 条件路由 → 专业Agent → 返回

from typing import TypedDict, Annotated, Literal
import asyncio

from langgraph.graph import StateGraph, END

from app.services.llm_service import chat_completion, stream_completion
from app.services.rag_service import build_rag_context


# ============ 状态定义 ============
class AgentState(TypedDict):
    """多智能体共享状态"""
    message: str          # 用户消息
    project_id: str       # 当前项目（可为空）
    chat_history: list    # 聊天历史
    intent: str           # 识别出的意图
    response: str         # 最终回复


# ============ 节点函数 ============

# 意图识别的系统提示词
INTENT_PROMPT = """你是任务调度器。判断用户消息的意图，只能返回以下之一：
- knowledge: 用户询问知识、技术问题、想了解资料（需要查知识库）
- experience: 用户想记录/查询开发经验、bug、解决方案
- interview: 用户想记录/分析面试、面试题
- document: 用户想生成/更新文档（README、PRD、简历等）
- chat: 普通对话

只返回意图单词，不要解释。"""


async def coordinator_node(state: AgentState) -> AgentState:
    """协调者：用LLM识别用户意图"""
    try:
        intent = await chat_completion(
            [], state["message"], INTENT_PROMPT
        )
        intent = intent.strip().lower()
        # 清理LLM可能输出的多余内容
        for valid in ["knowledge", "experience", "interview", "document", "chat"]:
            if valid in intent:
                intent = valid
                break
        else:
            intent = "chat"
    except Exception as e:
        print(f"意图识别失败: {e}")
        intent = "chat"

    return {"intent": intent}


async def knowledge_node(state: AgentState) -> AgentState:
    """知识Agent：RAG检索 + 基于知识库回答"""
    system_prompt = "你是CareerPilot的知识助手，请基于提供的资料回答用户问题。"

    # 项目聊天：检索知识库
    if state.get("project_id"):
        context = build_rag_context(state["project_id"], state["message"], top_k=3)
        if context:
            system_prompt += f"\n\n【知识库资料】\n{context}\n\n请优先基于资料回答。"

    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return {"response": response}


async def experience_node(state: AgentState) -> AgentState:
    """经验Agent：整理/查询开发经验"""
    system_prompt = (
        "你是CareerPilot的经验助手，帮助开发者整理开发经验和解决方案。"
        "如果用户想记录经验，请帮他把内容整理成清晰的格式：问题/原因/解决方案。"
        "如果用户想查询经验，请给出建议。"
    )
    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return {"response": response}


async def interview_node(state: AgentState) -> AgentState:
    """面试Agent：面试分析和建议"""
    system_prompt = (
        "你是CareerPilot的面试助手，帮助开发者分析面试表现、识别薄弱点、给出学习建议。"
        "如果用户描述面试问题，请分析并给出改进建议。"
    )
    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return {"response": response}


async def document_node(state: AgentState) -> AgentState:
    """文档Agent：生成项目文档"""
    system_prompt = (
        "你是CareerPilot的文档助手，帮助开发者生成高质量的文档（README、PRD、简历等）。"
        "请根据用户需求生成结构清晰、专业的文档内容。"
    )
    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return {"response": response}


async def chat_node(state: AgentState) -> AgentState:
    """普通对话Agent"""
    system_prompt = "你是CareerPilot AI助手，帮助开发者进行技术讨论和日常问答。"
    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return {"response": response}


# ============ 条件路由 ============
def route_by_intent(state: AgentState) -> str:
    """根据意图路由到对应Agent"""
    intent = state.get("intent", "chat")
    if intent in ("knowledge", "experience", "interview", "document"):
        return intent
    return "chat"


# ============ 构建图 ============
def build_agent_graph():
    """构建LangGraph工作流"""
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("experience", experience_node)
    workflow.add_node("interview", interview_node)
    workflow.add_node("document", document_node)
    workflow.add_node("chat", chat_node)

    # 设置入口
    workflow.set_entry_point("coordinator")

    # 条件路由：coordinator → 具体Agent
    workflow.add_conditional_edges(
        "coordinator",
        route_by_intent,
        {
            "knowledge": "knowledge",
            "experience": "experience",
            "interview": "interview",
            "document": "document",
            "chat": "chat",
        },
    )

    # 所有Agent执行完都结束
    for node in ["knowledge", "experience", "interview", "document", "chat"]:
        workflow.add_edge(node, END)

    return workflow.compile()


# 全局编译一次
agent_graph = build_agent_graph()


async def run_agent(message: str, project_id: str = "", chat_history: list = None) -> dict:
    """
    运行多智能体工作流
    返回: {"intent": "...", "response": "..."}
    """
    initial_state = {
        "message": message,
        "project_id": project_id,
        "chat_history": chat_history or [],
        "intent": "",
        "response": "",
    }
    result = await agent_graph.ainvoke(initial_state)
    return result
