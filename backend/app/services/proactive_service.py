# 主动成长服务 - AI主动识别薄弱点/文档提醒/知识库影响
# 核心价值: AI主动驱动成长，而非用户主动整理

from sqlalchemy.orm import Session
from app.models.learning_plan import LearningPlan
from app.models.notification import Notification
from app.models.interview import Interview, InterviewQuestion
from app.models.document import Document
from app.models.project_memory import ProjectMemory


# ============ 场景1: 面试薄弱点 → 学习计划 ============

async def analyze_interview_weakness(db: Session, project_id: str) -> list:
    """
    分析面试薄弱点，生成学习计划
    触发时机: 新增面试问题后
    """
    from collections import Counter
    from app.services.llm_service import structured_completion
    from app.agents.agent_schemas import LearningPlanOutput

    # 统计每个类别的弱次数（rating<=2）
    weak_questions = db.query(InterviewQuestion).join(Interview).filter(
        Interview.project_id == project_id,
        InterviewQuestion.rating <= 2,
        InterviewQuestion.category.isnot(None),
    ).all()

    if not weak_questions:
        return []

    # 按类别统计
    counter = Counter(q.category for q in weak_questions)

    # 找出薄弱>=2次的类别（重复暴露才是薄弱点）
    weak_categories = {cat: cnt for cat, cnt in counter.items() if cnt >= 2}
    if not weak_categories:
        return []

    # 组装弱点描述供LLM生成学习计划
    weak_desc = "\n".join(
        f"- {cat}: 薄弱{cnt}次" for cat, cnt in weak_categories.items()
    )
    # 收集相关弱问题
    weak_examples = [
        f"[{q.category}] {q.question}" for q in weak_questions[:5]
    ]
    examples_text = "\n".join(weak_examples)

    try:
        result = await structured_completion(
            LearningPlanOutput,
            f"薄弱领域：\n{weak_desc}\n\n弱问题示例：\n{examples_text}",
            "根据面试薄弱领域生成学习计划，每个薄弱类别一个计划，包含具体学习内容和建议资源。"
        )

        added = []
        for plan in result.plans:
            # 去重：同类别已有active计划则更新
            existing = db.query(LearningPlan).filter(
                LearningPlan.project_id == project_id,
                LearningPlan.category == plan.category,
                LearningPlan.status == "active",
            ).first()

            if existing:
                existing.content = plan.content
                existing.title = plan.title
                existing.weak_count = weak_categories.get(plan.category, existing.weak_count)
            else:
                new_plan = LearningPlan(
                    project_id=project_id,
                    category=plan.category,
                    title=plan.title,
                    content=plan.content,
                    weak_count=weak_categories.get(plan.category, 1),
                )
                db.add(new_plan)

            # 创建薄弱点提醒（去重：同项目同类别未读提醒不重复创建）
            existing_notif = db.query(Notification).filter(
                Notification.project_id == project_id,
                Notification.ntype == "weakness",
                Notification.is_read == False,  # noqa: E712
                Notification.title.like(f"%{plan.category}%"),
            ).first()

            if not existing_notif:
                notif = Notification(
                    project_id=project_id,
                    ntype="weakness",
                    title=f"📌 检测到{plan.category}薄弱",
                    content=f"面试中{plan.category}已薄弱{weak_categories.get(plan.category, 0)}次，已生成学习计划。",
                )
                db.add(notif)
            added.append(plan.category)

        db.commit()
        return added
    except Exception as e:
        print(f"学习计划生成失败: {e}")
        db.rollback()
        return []


# ============ 场景2: 项目变化 → 文档更新提醒 ============

async def check_document_updates(db: Session, project_id: str, trigger_context: str = "") -> list:
    """
    检测项目变化，提醒更新文档
    触发时机: 记忆沉淀后（技术决策/架构变化）
    """
    from app.services.llm_service import structured_completion
    from app.agents.agent_schemas import DocUpdateCheckOutput

    # 获取最近的技术决策记忆
    decisions = db.query(ProjectMemory).filter(
        ProjectMemory.project_id == project_id,
        ProjectMemory.memory_type.in_(["decision", "progress"]),
    ).order_by(ProjectMemory.created_at.desc()).limit(5).all()

    if not decisions:
        return []

    decisions_text = "\n".join(f"- {d.content}" for d in decisions)

    # 获取现有文档类型
    docs = db.query(Document).filter(Document.project_id == project_id).all()
    doc_types = [d.doc_type for d in docs] or ["readme"]

    try:
        result = await structured_completion(
            DocUpdateCheckOutput,
            f"项目最近的决策/进度：\n{decisions_text}\n\n现有文档：{', '.join(doc_types)}",
            "判断这些项目变化是否需要更新文档。需要则输出should_update=true和建议。"
        )

        added = []
        if result.should_update:
            notif = Notification(
                project_id=project_id,
                ntype="doc_update",
                title="📄 文档可能需要更新",
                content=result.reason,
            )
            db.add(notif)
            db.commit()
            added.append(notif)
        return added
    except Exception as e:
        print(f"文档更新检查失败: {e}")
        return []


# ============ 场景3: 知识库上传 → 影响分析 ============

async def analyze_knowledge_impact(db: Session, project_id: str, doc_content: str) -> list:
    """
    分析新上传文档对现有方案/面试的影响
    触发时机: 知识库上传完成后
    """
    from app.services.llm_service import structured_completion
    from app.agents.agent_schemas import KnowledgeImpactOutput

    if not doc_content or len(doc_content.strip()) < 50:
        return []

    # 获取现有经验标题作为"已有方案"
    from app.models.experience import Experience
    exps = db.query(Experience).filter(
        Experience.project_id == project_id
    ).order_by(Experience.created_at.desc()).limit(5).all()
    exp_titles = [e.title for e in exps]

    try:
        result = await structured_completion(
            KnowledgeImpactOutput,
            f"新上传文档内容（前500字）：\n{doc_content[:500]}",
            f"判断这份新资料是否会影响已有方案或面试回答。\n已有方案：{', '.join(exp_titles) if exp_titles else '暂无'}\n有影响则返回impact=true和建议。"
        )

        added = []
        if result.impact:
            notif = Notification(
                project_id=project_id,
                ntype="knowledge_impact",
                title="📚 新资料可能影响已有方案",
                content=result.reason,
            )
            db.add(notif)
            db.commit()
            added.append(notif)
        return added
    except Exception as e:
        print(f"知识库影响分析失败: {e}")
        return []


# ============ 查询 ============

def get_learning_plans(db: Session, project_id: str) -> list:
    """获取项目学习计划"""
    return db.query(LearningPlan).filter(
        LearningPlan.project_id == project_id,
        LearningPlan.status == "active",
    ).order_by(LearningPlan.weak_count.desc()).all()


def get_notifications(db: Session, project_id: str, unread_only: bool = False, limit: int = 20) -> list:
    """获取项目提醒"""
    query = db.query(Notification).filter(Notification.project_id == project_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def mark_notification_read(db: Session, notif_id: str) -> bool:
    """标记提醒已读"""
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        return False
    notif.is_read = True
    db.commit()
    return True
