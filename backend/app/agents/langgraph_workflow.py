# LangGraph 多智能体工作流（V2优化版）
# 架构: Coordinator(意图识别) → 条件路由 → 专业Agent(调用真实工具) → 返回
# 特性: Agent真实操作数据库 + 执行过程记录 + 工具选择

from typing import TypedDict
import time
from sqlalchemy.orm import Session

from langgraph.graph import StateGraph, END

from app.services.llm_service import chat_completion, structured_completion
from app.services.rag_service import build_rag_context
from app.agents.agent_schemas import IntentOutput, ToolCallOutput, ExperienceExtractOutput
from app.agents.agent_tools import (
    save_experience, get_recent_experiences,
    get_interview_stats, save_document, get_document,
    search_project_knowledge, TOOL_DESCRIPTIONS,
)
from app.models.agent_execution import AgentExecution


# ============ 状态定义 ============
class AgentState(TypedDict):
    """多智能体共享状态"""
    message: str          # 用户消息
    project_id: str       # 当前项目（可为空）
    chat_history: list    # 聊天历史
    db: object            # 数据库会话
    intent: str           # 识别出的意图
    response: str         # 最终回复
    execution_log: list   # 执行过程日志


# ============ 执行记录 ============

def _record_execution(db, agent_type: str, input_data: dict,
                      output_data: dict, duration_ms: int, status: str = "success"):
    """记录Agent执行过程到数据库"""
    if db is None:
        return
    try:
        exec_record = AgentExecution(
            agent_type=agent_type,
            input_data=input_data,
            output_data={"response_preview": str(output_data.get("response", ""))[:200]},
            duration_ms=duration_ms,
            status=status,
        )
        db.add(exec_record)
        db.commit()
    except Exception as e:
        print(f"记录Agent执行失败: {e}")
        db.rollback()


# ============ 节点函数 ============

# 意图识别提示词（结构化）
INTENT_PROMPT = """你是任务调度器。判断用户消息的意图，只返回以下之一：
- knowledge: 询问技术知识、想了解资料（查知识库）
- experience: 记录/查询开发经验、bug、解决方案
- interview: 记录/分析面试、面试题、薄弱点
- document: 生成/更新文档（README、PRD、简历）
- chat: 普通对话

只返回意图单词，不要解释。"""

# 工具选择提示词
TOOL_SELECT_PROMPT = """你是{agent_name}，负责处理用户的请求。

可用工具：
{tool_descriptions}

判断用户请求是否需要调用工具：
- 如果需要（记录/查询/保存类请求）→ 输出: TOOL:工具名(参数=值, 参数2=值)
- 如果不需要（纯咨询/建议类）→ 输出: NONE

只输出一行，不要解释。"""


async def coordinator_node(state: AgentState) -> AgentState:
    """协调者：结构化LLM识别用户意图"""
    start = time.time()
    try:
        # 结构化输出意图（Pydantic schema约束，比文本匹配稳定）
        intent_result = await structured_completion(
            IntentOutput,
            state["message"],
            "判断用户消息的意图：knowledge=技术知识/查资料, experience=记录查询经验, interview=面试分析, document=生成文档, chat=普通对话。project_related=是否涉及项目内数据。"
        )
        intent = intent_result.intent
        confidence = intent_result.confidence
        # 低置信度兜底
        if confidence < 0.4:
            intent = "chat"
    except Exception as e:
        print(f"意图识别失败: {e}")
        intent = "chat"

    _record_execution(state.get("db"), "coordinator",
                      {"message": state["message"]},
                      {"intent": intent},
                      int((time.time() - start) * 1000))
    return {"intent": intent}


async def _agent_with_tools(state: AgentState, agent_name: str,
                            tool_map: dict, base_prompt: str) -> AgentState:
    """通用Agent执行器：结构化判断工具 → 结构化提取参数 → 执行 → 回复"""
    start = time.time()
    message = state["message"]
    db = state.get("db")
    project_id = state.get("project_id")
    response = ""

    # 0. 注入项目长期记忆（跨会话回忆）
    memory_prompt = ""
    if db is not None and project_id:
        try:
            from app.services.memory_service import build_memory_prompt
            memory_prompt = build_memory_prompt(db, project_id)
        except Exception as e:
            print(f"记忆注入失败: {e}")

    # 1. 构建工具描述
    available_tools = {k: v for k, v in TOOL_DESCRIPTIONS.items() if k in tool_map}
    tool_desc = "\n".join(f"- {name}: {desc}" for name, desc in available_tools.items())

    try:
        # 2. 结构化判断是否调用工具（ToolCallOutput schema）
        decision = await structured_completion(
            ToolCallOutput,
            message,
            f"你是{agent_name}助手。判断用户请求是否需要调用工具。\n可用工具：\n{tool_desc}\n"
            f"use_tool=true时指定tool和arguments（工具参数从用户消息中提取）。"
        )

        if decision.use_tool and decision.tool in tool_map and db is not None and project_id:
            # 3. 使用结构化参数（ToolCallOutput.arguments 已由LLM提取）
            tool_name = decision.tool
            tool_args = dict(decision.arguments or {})

            # 经验保存：把arguments里的字段映射到save_experience参数
            if tool_name == "save_experience":
                tool_args = {
                    "title": tool_args.get("title") or tool_args.get("标题") or message[:30],
                    "exp_type": tool_args.get("exp_type") or tool_args.get("type") or "note",
                    "content": tool_args.get("content") or message,
                    "solution": tool_args.get("solution"),
                }

            tool_args["db"] = db
            tool_args["project_id"] = project_id

            # 4. 执行工具（兼容dict和list返回）
            tool_result = tool_map[tool_name](**tool_args)
            if isinstance(tool_result, dict):
                response = tool_result.get("message", str(tool_result))
            elif isinstance(tool_result, list) and tool_result:
                response = f"查询到 {len(tool_result)} 条记录：\n" + "\n".join(
                    str(item) for item in tool_result[:5]
                )
            elif not tool_result:
                # 工具无结果：注入项目记忆再回答（跨会话回忆）
                response = await _answer_with_memory(state, agent_name, base_prompt, memory_prompt)
            else:
                response = str(tool_result)

            _record_execution(db, f"{agent_name}(tool:{tool_name})",
                              {"message": message}, {"result": response},
                              int((time.time() - start) * 1000))
        else:
            # 5. 无工具调用 → 直接咨询回复
            system_prompt = base_prompt
            # 项目上下文增强（按Agent类型注入不同数据）
            if db is not None and project_id:
                # 长期记忆注入（跨会话）
                if memory_prompt:
                    system_prompt += f"\n\n{memory_prompt}"
                # 项目当前数据
                ctx = _build_project_context(db, project_id, message, agent_name)
                if ctx:
                    system_prompt += f"\n\n【项目当前数据】\n{ctx}"

            response = await chat_completion(
                state.get("chat_history", []), message, system_prompt
            )
            _record_execution(db, agent_name, {"message": message},
                              {"response": response[:200]},
                              int((time.time() - start) * 1000))

    except Exception as e:
        print(f"{agent_name}执行失败: {e}")
        response = "（处理失败，请重试）"
        _record_execution(db, agent_name, {"message": message},
                          {"error": str(e)}, int((time.time() - start) * 1000), "failed")

    return {"response": response}


async def _answer_with_memory(state: AgentState, agent_name: str,
                              base_prompt: str, memory_prompt: str) -> str:
    """工具无结果时，注入项目记忆生成回复"""
    system_prompt = base_prompt
    if memory_prompt:
        system_prompt += (
            f"\n\n以下是该项目的历史记忆，用户可能在问项目历史问题，请结合记忆回答：\n{memory_prompt}"
        )
    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return response


def _build_project_context(db: Session, project_id: str, message: str, agent_name: str = "") -> str:
    """按Agent类型注入项目上下文：经验/面试/知识库"""
    parts = []

    # 经验Agent：注入更多经验数据
    if agent_name in ("experience", "chat", ""):
        try:
            exps = get_recent_experiences(db, project_id, limit=5)
            if exps:
                parts.append("项目最近经验:\n" + "\n".join(f"- {e['title']}({e['type']})" for e in exps))
        except Exception:
            pass

    # 面试Agent：注入完整面试统计
    if agent_name in ("interview", "chat", ""):
        try:
            stats = get_interview_stats(db, project_id)
            if stats["total_interviews"] > 0:
                parts.append(f"面试统计: 共{stats['total_interviews']}场/{stats['total_questions']}题")
                if stats["weak_areas"]:
                    parts.append("面试薄弱点: " + ", ".join(
                        f"{w['category']}({w['weak_count']}次弱)" for w in stats["weak_areas"]
                    ))
        except Exception:
            pass

    # 知识Agent：注入RAG检索
    if agent_name in ("knowledge", "chat", ""):
        try:
            context = build_rag_context(project_id, message, top_k=3)
            if context:
                parts.append("知识库相关:\n" + context[:400])
        except Exception:
            pass

    # 文档Agent：注入现有文档
    if agent_name in ("document", "chat", ""):
        try:
            from app.models.document import Document
            docs = db.query(Document).filter(Document.project_id == project_id).all()
            if docs:
                parts.append("项目现有文档: " + ", ".join(f"{d.doc_type}(v{d.version})" for d in docs))
        except Exception:
            pass

    return "\n\n".join(parts)


# ============ 具体Agent节点 ============

async def knowledge_node(state: AgentState) -> AgentState:
    """知识Agent：RAG检索 + 知识库工具"""
    return await _agent_with_tools(
        state, "knowledge",
        {"search_project_knowledge": search_project_knowledge},
        "你是CareerPilot的知识助手，基于项目知识库回答技术问题。"
    )


async def experience_node(state: AgentState) -> AgentState:
    """经验Agent：写/查开发经验"""
    return await _agent_with_tools(
        state, "experience",
        {"save_experience": save_experience, "get_recent_experiences": get_recent_experiences},
        "你是CareerPilot的经验助手。用户想记录经验时调用save_experience，想查看时调用get_recent_experiences，纯咨询则直接回答。"
    )


async def interview_node(state: AgentState) -> AgentState:
    """面试Agent：分析面试/薄弱点"""
    return await _agent_with_tools(
        state, "interview",
        {"get_interview_stats": get_interview_stats},
        "你是CareerPilot的面试助手，分析面试表现、识别薄弱点、给学习建议。用户问面试情况时调用get_interview_stats。"
    )


async def document_node(state: AgentState) -> AgentState:
    """文档Agent：生成/保存文档"""
    return await _agent_with_tools(
        state, "document",
        {"save_document": save_document, "get_document": get_document},
        "你是CareerPilot的文档助手，生成高质量的README/PRD/简历。用户要求生成时调用save_document。"
    )


async def chat_node(state: AgentState) -> AgentState:
    """普通对话Agent（注入项目长期记忆）"""
    system_prompt = "你是CareerPilot AI助手，帮助开发者进行技术讨论和日常问答。"

    # 注入项目长期记忆（跨会话回忆）
    db = state.get("db")
    project_id = state.get("project_id")
    if db is not None and project_id:
        try:
            from app.services.memory_service import build_memory_prompt
            memory_prompt = build_memory_prompt(db, project_id)
            if memory_prompt:
                system_prompt += f"\n\n以下是该项目的历史记忆，回答时请结合这些信息（如果用户问的是项目历史相关问题，请直接引用记忆回答）：\n{memory_prompt}"
        except Exception as e:
            print(f"chat记忆注入失败: {e}")

    response = await chat_completion(
        state.get("chat_history", []), state["message"], system_prompt
    )
    return {"response": response}


# ============ 条件路由 ============
def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "chat")
    if intent in ("knowledge", "experience", "interview", "document"):
        return intent
    return "chat"


# ============ 构建图 ============
def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("experience", experience_node)
    workflow.add_node("interview", interview_node)
    workflow.add_node("document", document_node)
    workflow.add_node("chat", chat_node)

    workflow.set_entry_point("coordinator")

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

    for node in ["knowledge", "experience", "interview", "document", "chat"]:
        workflow.add_edge(node, END)

    return workflow.compile()


agent_graph = build_agent_graph()


async def run_agent(message: str, project_id: str = "", chat_history: list = None,
                    db: Session = None) -> dict:
    """
    运行多智能体工作流
    db: 数据库会话（Agent操作数据库需要）
    返回: {"intent": "...", "response": "...", "execution_log": [...]}
    """
    initial_state = {
        "message": message,
        "project_id": project_id,
        "chat_history": chat_history or [],
        "db": db,
        "intent": "",
        "response": "",
        "execution_log": [],
    }
    result = await agent_graph.ainvoke(initial_state)
    return result
