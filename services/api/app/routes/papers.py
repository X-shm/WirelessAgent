"""Paper routes — Agent2Paper: list/search papers + virtual-author Q&A."""
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, async_session
from app.models.paper import Paper
from app.models.paper_message import PaperMessage
from app.services.paper_service import refresh_papers, build_author_prompt
from app.services.openclaw_client import openclaw
from app.limiter import limiter
from pydantic import BaseModel

router = APIRouter(prefix="/api/papers", tags=["papers"])

_MIN_REFRESH_INTERVAL = 300
_last_refresh = 0.0


class AskRequest(BaseModel):
    question: str


def paper_out(p: Paper) -> dict:
    return {
        "arxiv_id": p.arxiv_id,
        "title": p.title,
        "title_zh": p.title_zh,
        "authors": p.authors,
        "abstract": p.abstract,
        "abstract_zh": p.abstract_zh,
        "keywords": p.keywords,
        "primary_category": p.primary_category,
        "published": p.published,
        "link": p.link,
    }


@router.post("/refresh")
async def refresh(
    request: Request,
    days: int = Query(7, ge=1, le=30),
    max_papers: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    global _last_refresh
    now = time.time()
    if now - _last_refresh < _MIN_REFRESH_INTERVAL:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limited. Try again in {int(_MIN_REFRESH_INTERVAL - (now - _last_refresh))} seconds.",
        )
    _last_refresh = now
    try:
        return await refresh_papers(db, days=days, max_papers=max_papers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {e}")


@router.get("/")
async def list_papers(
    q: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Paper)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            Paper.title.ilike(like) | Paper.title_zh.ilike(like) | Paper.abstract.ilike(like)
        )
    if category:
        stmt = stmt.where(Paper.primary_category == category)
    stmt = stmt.order_by(Paper.published.desc(), Paper.created_at.desc()).limit(limit).offset(offset)
    rows = (await db.execute(stmt)).scalars().all()
    return [paper_out(p) for p in rows]


@router.get("/{arxiv_id}")
async def get_paper(arxiv_id: str, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper_out(row)


@router.get("/{arxiv_id}/messages")
async def get_paper_messages(arxiv_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(PaperMessage)
            .where(PaperMessage.arxiv_id == arxiv_id, PaperMessage.user_id == request.state.user_id)
            .order_by(PaperMessage.created_at)
        )
    ).scalars().all()
    return [{"role": m.role, "content": m.content} for m in rows]


@router.post("/{arxiv_id}/ask")
@limiter.limit("1/second")
async def ask_author(
    arxiv_id: str,
    req: AskRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = request.state.user_id
    paper = (await db.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.add(PaperMessage(user_id=user_id, arxiv_id=arxiv_id, role="user", content=req.question))
    await db.commit()

    rows = (
        await db.execute(
            select(PaperMessage)
            .where(PaperMessage.arxiv_id == arxiv_id, PaperMessage.user_id == user_id)
            .order_by(PaperMessage.created_at)
        )
    ).scalars().all()
    messages = [{"role": m.role, "content": m.content} for m in rows]
    system_prompt = build_author_prompt(paper)
    oc_user = f"paper:{arxiv_id}:{user_id}"

    async def generate():
        full = ""
        try:
            async for token in openclaw.chat_stream(messages, system_prompt=system_prompt, user_id=oc_user):
                full += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            msg = str(e).lower()
            if "timeout" in msg or "timed out" in msg:
                err = "回复生成超时，请稍后重试"
            elif "connection" in msg or "refused" in msg:
                err = "AI 服务暂时不可用，请稍后重试 📡"
            else:
                err = f"服务异常：{str(e)}"
            yield f"data: {json.dumps({'error': err})}\n\n"

        if full:
            async with async_session() as s:
                s.add(PaperMessage(user_id=user_id, arxiv_id=arxiv_id, role="assistant", content=full))
                await s.commit()
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
