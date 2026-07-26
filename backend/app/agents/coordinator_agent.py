# Coordinator Agent - 统一调度，理解用户意图

from app.agents.base_agent import BaseAgent


class CoordinatorAgent(BaseAgent):
    """
    调度Agent - 整个系统的大脑
    - 理解用户意图
    - 制定执行计划
    - 调度其他Agent
    """

    def __init__(self):
        super().__init__()
        # 意图关键词映射
        self.intent_keywords = {
            "knowledge": ["知识", "文档", "搜索", "查询", "RAG"],
            "experience": ["经验", "bug", "问题", "解决方案", "踩坑"],
            "interview": ["面试", "面试题", "面试官", "offer", "面试准备"],
            "document": ["README", "PRD", "简历", "文档生成", "STAR"],
            "chat": ["聊天", "对话", "讨论"]
        }

    async def execute(self, input_data: dict) -> dict:
        """
        分析用户意图并调度Agent
        """
        user_message = input_data.get("content", "")

        # 1. 分析意图
        intent = self.analyze_intent(user_message)
        self.log(f"识别意图: {intent}")

        # 2. 返回调度结果
        return {
            "intent": intent,
            "agent": intent,
            "message": user_message,
            "needs_context": intent in ["knowledge", "experience"]
        }

    def analyze_intent(self, message: str) -> str:
        """分析用户意图"""
        message_lower = message.lower()

        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent

        # 默认返回chat
        return "chat"
