"""
经验沉淀 Skill - 把对话中的问题+答案自动沉淀为开发经验
触发: 每轮对话后自动尝试，或用户说"沉淀这个经验/记录这个"
"""

from app.skills.base import Skill
from app.agents.agent_schemas import ExperienceExtractOutput
from app.services.llm_service import structured_completion
from app.agents.agent_tools import save_experience


class ExperienceCurator(Skill):
    """经验沉淀师：从对话中提取问题+答案，写入 experiences 表"""

    name = "experience_curator"
    description = "把对话中的问题与答案沉淀为开发经验。当对话中有明确的技术问题与解答时自动触发。"

    async def execute(self, state: dict) -> str:
        """
        执行沉淀：
        1. 检查是否有"问题+答案"（用户问了技术问题，AI给了回答）
        2. 用 LLM 结构化提取：问题 / 答案
        3. 调用 save_experience 写入 experiences 表
        4. 返回确认信息
        """
        message = state.get("message", "")
        db = state.get("db")
        project_id = state.get("project_id")
        chat_history = state.get("chat_history", [])

        # 没有项目上下文就无法归属经验
        if not db or not project_id:
            return "沉淀经验需要项目上下文，请先在左侧选择一个项目"

        # 组装"问题 + 最近回答"上下文，供LLM判断是否有价值沉淀
        conv_text = f"用户问题: {message}\n"
        if chat_history:
            # 取最后一条AI回答作为"答案"
            for msg in reversed(chat_history[-6:]):
                if msg.get("role") == "assistant":
                    conv_text += f"AI回答: {msg.get('content', '')[:500]}"
                    break

        # 用结构化schema提取经验字段
        try:
            exp = await structured_completion(
                ExperienceExtractOutput,
                conv_text,
                "把用户的技术问题沉淀为一条开发经验。"
                "title=问题主题(一句话)，exp_type=类型(lesson/note/bug/solution)，"
                "content=问题详细描述，solution=解答要点。"
            )
        except Exception as e:
            print(f"经验提取失败: {e}")
            return "这次对话不适合沉淀为经验"

        # 写入 experiences 表
        result = save_experience(
            db, project_id,
            title=exp.title,
            exp_type=exp.exp_type,
            content=exp.content,
            solution=exp.solution,
        )
        return f"✅ {result['message']}"
