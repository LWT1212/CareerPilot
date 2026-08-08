"""
Skill 管理器 - 注册/匹配/执行专业技能
"""

from app.skills.base import Skill


class SkillsManager:
    """技能管理器"""

    def __init__(self):
        self._skills = {}  # {技能名: Skill实例}

    def register(self, skill: Skill):
        """注册一个技能"""
        self._skills[skill.name] = skill

    def match(self, message: str) -> Skill | None:
        """
        根据用户消息判断是否命中某个技能
        目前用关键词匹配（后续可升级为LLM判断）
        """
        # 触发词表：技能名 → 关键词
        trigger_keywords = {
            "experience_curator": ["沉淀", "记录经验", "保存经验", "记下来"],
        }

        for skill_name, keywords in trigger_keywords.items():
            if skill_name in self._skills:
                for kw in keywords:
                    if kw in message:
                        return self._skills[skill_name]
        return None

    async def execute(self, skill_name: str, state: dict) -> str:
        """执行指定技能"""
        skill = self._skills.get(skill_name)
        if not skill:
            return f"技能 {skill_name} 不存在"
        return await skill.execute(state)

    def list_skills(self) -> list[str]:
        """列出所有技能名"""
        return list(self._skills.keys())


# 全局单例（注册所有Skill）
skills_manager = SkillsManager()


def register_all_skills():
    """注册所有内置技能"""
    from app.skills.experience_curator import ExperienceCurator
    skills_manager.register(ExperienceCurator())


# 导入时自动注册
register_all_skills()
