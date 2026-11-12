"""业务工具：知识库检索 / 论文 / 项目 / 任务 / 文件。"""
from datetime import datetime, timezone

from sqlalchemy import select

from app.agent.tools.registry import Tool, ToolContext, ToolRegistry
from app.agent.memory import memory_store
from app.database import async_session
from app.models.file import File
from app.models.paper import Paper
from app.models.project import Project
from app.models.task import Task
from app.services.rag_service import rag
from app.task_status import TaskStatus, ensure_transition


async def _rag_search(args: dict, ctx: ToolContext) -> dict:
    q = (args.get("q") or args.get("query") or "").strip()
    if not q:
        return {"error": "缺少查询词 q"}
    top_k = int(args.get("top_k", 5) or 5)
    try:
        hits = await rag.search(q, top_k)
    except Exception as e:  # noqa: BLE001
        return {"error": f"知识库检索失败: {e}", "results": []}
    return {"query": q, "results": hits, "total": len(hits)}


async def _paper_search(args: dict, ctx: ToolContext) -> dict:
    q = (args.get("q") or "").strip()
    limit = min(int(args.get("limit", 5) or 5), 20)
    async with async_session() as db:
        stmt = select(Paper)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                Paper.title.ilike(like) | Paper.title_zh.ilike(like) | Paper.abstract.ilike(like)
            )
        stmt = stmt.order_by(Paper.published.desc(), Paper.created_at.desc()).limit(limit)
        rows = (await db.execute(stmt)).scalars().all()
    return {
        "papers": [
            {
                "arxiv_id": p.arxiv_id,
                "title": p.title,
                "title_zh": p.title_zh,
                "abstract": (p.abstract or "")[:300],
                "primary_category": p.primary_category,
            }
            for p in rows
        ]
    }


async def _project_list(args: dict, ctx: ToolContext) -> dict:
    async with async_session() as db:
        rows = (
            await db.execute(
                select(Project).where(Project.user_id == ctx.user_id).order_by(Project.updated_at.desc())
            )
        ).scalars().all()
    return {"projects": [{"id": p.id, "name": p.name, "description": p.description} for p in rows]}


async def _project_create(args: dict, ctx: ToolContext) -> dict:
    name = (args.get("name") or "").strip()
    if not name:
        return {"error": "项目名称不能为空"}
    description = args.get("description")
    async with async_session() as db:
        project = Project(user_id=ctx.user_id, name=name, description=description)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return {"id": project.id, "name": project.name, "description": project.description}


async def _task_list(args: dict, ctx: ToolContext) -> dict:
    async with async_session() as db:
        stmt = select(Task).where(Task.user_id == ctx.user_id)
        project_id = args.get("project_id")
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)
        stmt = stmt.order_by(Task.created_at.desc()).limit(50)
        rows = (await db.execute(stmt)).scalars().all()
    return {
        "tasks": [
            {"id": t.id, "type": t.type, "status": t.status, "project_id": t.project_id} for t in rows
        ]
    }


async def _task_create(args: dict, ctx: ToolContext) -> dict:
    task_type = (args.get("type") or "").strip()
    if not task_type:
        return {"error": "任务类型不能为空"}
    parameters = args.get("parameters") or {}
    project_id = args.get("project_id")
    async with async_session() as db:
        if project_id:
            obj = await db.get(Project, project_id)
            if obj is None or obj.user_id != ctx.user_id:
                return {"error": "项目不存在或无权访问"}
        task = Task(user_id=ctx.user_id, project_id=project_id, type=task_type, parameters=parameters)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        task.status = ensure_transition(task.status, TaskStatus.queued.value).value
        task.queued_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.commit()
        return {"id": task.id, "type": task.type, "status": task.status, "project_id": task.project_id}


async def _file_list(args: dict, ctx: ToolContext) -> dict:
    async with async_session() as db:
        rows = (
            await db.execute(
                select(File).where(File.user_id == ctx.user_id).order_by(File.created_at.desc())
            )
        ).scalars().all()
    return {
        "files": [
            {"id": f.id, "filename": f.filename, "size": f.size, "content_type": f.content_type}
            for f in rows
        ]
    }


async def _save_memory(args: dict, ctx: ToolContext) -> dict:
    key = (args.get("key") or "").strip()
    content = (args.get("content") or "").strip()
    if not key or not content:
        return {"error": "key 与 content 均不能为空"}
    importance = int(args.get("importance", 0) or 0)
    mem = await memory_store.add(ctx.user_id, key, content, importance)
    return {"saved": True, "key": mem["key"]}


def register_builtin(reg: ToolRegistry) -> None:
    reg.register(
        Tool(
            name="rag_search",
            description="在本地无线通信知识库中检索相关资料，返回最相关的文本片段。",
            parameters={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "检索关键词或问题"},
                    "top_k": {"type": "integer", "description": "返回条数，默认 5"},
                },
                "required": ["q"],
            },
            handler=_rag_search,
        )
    )
    reg.register(
        Tool(
            name="paper_search",
            description="检索 arXiv 论文库（标题/摘要模糊匹配），返回论文元数据。",
            parameters={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "标题或摘要关键词"},
                    "limit": {"type": "integer", "description": "返回条数，默认 5，最大 20"},
                },
                "required": [],
            },
            handler=_paper_search,
        )
    )
    reg.register(
        Tool(
            name="project_list",
            description="列出当前用户的所有项目。",
            parameters={"type": "object", "properties": {}, "required": []},
            handler=_project_list,
        )
    )
    reg.register(
        Tool(
            name="project_create",
            description="创建一个新项目。",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "项目名称"},
                    "description": {"type": "string", "description": "项目描述（可选）"},
                },
                "required": ["name"],
            },
            handler=_project_create,
        )
    )
    reg.register(
        Tool(
            name="task_list",
            description="列出当前用户的任务（可按项目过滤）。",
            parameters={
                "type": "object",
                "properties": {"project_id": {"type": "string", "description": "项目 ID（可选）"}},
                "required": [],
            },
            handler=_task_list,
        )
    )
    reg.register(
        Tool(
            name="task_create",
            description="创建一个后台任务（当前版本仅登记，暂不执行）。",
            parameters={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "任务类型"},
                    "parameters": {"type": "object", "description": "任务参数（可选）"},
                    "project_id": {"type": "string", "description": "所属项目 ID（可选）"},
                },
                "required": ["type"],
            },
            handler=_task_create,
        )
    )
    reg.register(
        Tool(
            name="file_list",
            description="列出当前用户已上传的文件。",
            parameters={"type": "object", "properties": {}, "required": []},
            handler=_file_list,
        )
    )
    reg.register(
        Tool(
            name="save_memory",
            description="把关于用户的重要偏好、事实或上下文写入长期记忆，供后续会话自动注入。",
            parameters={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "记忆的简短标签，如「研究方向」"},
                    "content": {"type": "string", "description": "要记住的具体内容"},
                    "importance": {"type": "integer", "description": "重要程度 0-10，默认 0"},
                },
                "required": ["key", "content"],
            },
            handler=_save_memory,
        )
    )
