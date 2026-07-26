# Document Agent - 文档生成

from app.agents.base_agent import BaseAgent


class DocumentAgent(BaseAgent):
    """
    文档Agent - 负责文档生成
    - 生成README
    - 生成PRD
    - 生成简历
    - 生成STAR描述
    """

    # 文档模板
    TEMPLATES = {
        "readme": "# {project_name}\n\n## 简介\n\n{description}\n\n## 功能特性\n\n...\n\n## 技术栈\n\n...\n\n## 快速开始\n\n...",
        "prd": "# 产品需求文档\n\n## 项目背景\n\n...\n\n## 目标用户\n\n...\n\n## 功能需求\n\n...",
        "star": "# {project_name}\n\n## Situation（情境）\n\n...\n\n## Task（任务）\n\n...\n\n## Action（行动）\n\n...\n\n## Result（结果）\n\n...",
    }

    async def execute(self, input_data: dict) -> dict:
        doc_type = input_data.get("doc_type", "readme")
        project_name = input_data.get("project_name", "Project")
        description = input_data.get("description", "")

        self.log(f"生成文档: {doc_type}")

        return {
            "agent": "document",
            "doc_type": doc_type,
            "content": self.generate(doc_type, project_name, description)
        }

    def generate(self, doc_type: str, project_name: str, description: str) -> str:
        """生成文档内容"""
        template = self.TEMPLATES.get(doc_type, "# {project_name}\n\n{description}")
        return template.format(
            project_name=project_name,
            description=description or "待补充"
        )
