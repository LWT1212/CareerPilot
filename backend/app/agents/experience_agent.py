# Experience Agent - 开发经验整理

from app.agents.base_agent import BaseAgent


class ExperienceAgent(BaseAgent):
    """
    经验Agent - 负责开发经验管理
    - 整理经验
    - 生成成长记录
    - 问题分类
    """

    async def execute(self, input_data: dict) -> dict:
        action = input_data.get("action", "query")
        content = input_data.get("content", "")

        self.log(f"执行经验操作: {action}")

        if action == "organize":
            return await self.organize(content)
        else:
            return {"agent": "experience", "response": "经验查询结果..."}

    async def organize(self, content: str) -> dict:
        """整理经验"""
        return {
            "agent": "experience",
            "action": "organize",
            "response": f"已整理经验: {content[:100]}...",
            "tags": ["bug", "solution"]
        }
