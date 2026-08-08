"""
Skill 基类 - 专业技能包的通用结构
"""

from abc import ABC, abstractmethod


class Skill(ABC):
    """技能基类"""
    name: str = ""              # 技能名
    description: str = ""       # 何时触发（给路由判断）

    def __init__(self):
        self.name = self.name or self.__class__.__name__

    @abstractmethod
    async def execute(self, state: dict) -> str:
        """
        执行技能
        - state: 当前对话状态（message/project_id/db/chat_history）
        - 返回: 技能处理结果（给用户看的回复）
        """
        pass
