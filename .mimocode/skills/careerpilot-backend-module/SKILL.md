---
name: careerpilot-backend-module
description: "CareerPilot-specific playbook for adding a new backend module. Use when the user asks to create or extend a backend feature/module in this project (e.g. a new model, API, CRUD module, or agent) — or says things like '下一步' during backend development. Follows the established per-module phase pattern: model → schema → service → API router → wire into __init__.py + main.py → restart uvicorn → verify /docs → add tests → commit. Also handles the guided-learning mode where the user executes commands themselves. Do NOT use for frontend work or general FastAPI questions."
---

# CareerPilot 后端模块开发流程

在 `/home/magic/pyproject/Assistant/backend/` 中按既定的 phase 模式添加或扩展一个后端模块。此模式已经在 auth / project / chat / knowledge / experience / interview / document / agent 八个模块上重复过，照抄即可。

## 项目约束（先读，别跳）

- 技术栈: FastAPI 0.109 + SQLAlchemy + SQLite（`backend/careerpilot.db`）
- 虚拟环境: `/home/magic/pyproject/Assistant/.venv`，所有命令先 `source ../.venv/bin/activate`
- 该用户是**引导式学习**模式: 用户常要求“下一步”“告诉我为什么”“代码是什么意思”。若用户没有明确说“直接弄”，就给出命令让用户自己执行，并解释每一步为什么这样做。
- 每完成一个模块必须更新开发日志（`enterprise-dev-journal` skill → `docs/journal/`），提交信息用 `feat(<module>): 完成XXX模块`。
- GitHub push 偶尔超时：push 失败时告知用户从终端手动 `git push origin main`。

## 标准步骤（每模块 8 步）

### 1. 建模型 `backend/app/models/<module>.py`
- 继承 `Base`（来自 `app.db`），字段类型对齐 `docs/database-design.md`。
- 表名默认小写复数，外键用 `project_id` 关联项目。
- 不要在模型里用 `metadata` 作为 JSON 列名（SQLAlchemy 保留字），用 `extra_data` / `msg_metadata`。

### 2. 更新 `backend/app/models/__init__.py`
必须把新模型加进去并加入 `__all__`——空 `__init__.py` 会导致 SQLAlchemy 不建表。这是最容易漏的一步。

### 3. 建 Schema `backend/app/schemas/<module>.py`
- 命名约定：`<Xxx>Create` / `<Xxx>Update` / `<Xxx>Response`。
- 直接从 `app.schemas.<module>` 导入即可（见第 5 步），不必同步改 `schemas/__init__.py`——现有经验/interview/document 模块就没改它。

### 4. 建 Service `backend/app/services/<module>_service.py`
- 函数命名：`create_<module>` / `get_<module>` / `get_<module>s` / `update_<module>` / `delete_<module>`。
- 第一个参数都是 `db: Session`，然后是 `project_id` / 业务参数；先 `db.add` → `db.commit` → `db.refresh`。

### 5. 建 API Router `backend/app/api/v1/<module>.py`
- 模式照抄 `experiences.py`：`APIRouter(prefix="/projects/{project_id}/<modules>", tags=["<中文标签>"])`。
- 导入 schema/service 用相对模块路径；`response_model` 用对应 Response。
- 找不到记录时 `raise HTTPException(status_code=404, detail="...")`。

### 6. 接线：`api/v1/__init__.py` + `app/main.py`
- `api/v1/__init__.py`: `from app.api.v1.<module> import router as <module>_router`，并加入 `__all__`。
- `app/main.py`: import 该 router（以及子 router，如 message_router/question_router），并 `app.include_router(<module>_router, prefix="/api/v1")`。

### 7. 重启并验证
```bash
pkill -f uvicorn 2>/dev/null; sleep 1
cd /home/magic/pyproject/Assistant/backend && source ../.venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 2
curl -s http://127.0.0.1:8000/health
```
然后让用户在浏览器打开 `http://127.0.0.1:8000/docs` 验证新接口。旧 DB（`backend/careerpilot.db`）只有在 schema 结构变化导致启动报错时才删除重建，否则保留数据。

### 8. 补测试（可选但强烈推荐）
- 模式：`backend/tests/conftest.py` 已提供 `client` / `db` fixture（TestClient + 内存 SQLite）。
- 新建 `backend/tests/test_<module>.py`，每个测试**先通过 API 创建项目**再测 CRUD（见 `test_interviews.py`）。
- 运行必须用：`cd backend && source ../.venv/bin/activate && python -m pytest tests/ -v`（直接用 `pytest` 会误用 anaconda 系统 Python）。

## 提交约定

```bash
git add -A
git commit -m "feat(<module>): 完成XXX模块

- 创建模型 (models/<module>.py)
- 创建Schema (schemas/<module>.py)
- 创建服务 (services/<module>_service.py)
- 创建API (api/v1/<module>.py)"
git push origin main   # 超时就提示用户手动 push
```

测试提交用 `test: 添加XXX模块单元测试`；日志提交用 `docs(journal): ...`。每步之后都要同步更新 `docs/journal/JOURNAL.md`（概览表 + 详细步骤）和 `ERRORS.md`（新错误）。

## 停止条件

- 新模块在 `/docs` 可调通，测试通过（如加了），已 commit + push，且 journal 已更新。
- 完成即停，不要顺手做下一个模块——用户喜欢一步一步来。
