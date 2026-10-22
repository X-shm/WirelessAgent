"""Paper service — fetch, translate, persist papers; build virtual-author prompts."""
import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.paper import Paper


def _digest_scripts_dir() -> str:
    return os.path.join(settings.arxiv_digest_dir, "scripts")


def _sync_fetch_and_translate(days: int, max_papers: int) -> dict:
    """Blocking: fetch papers from arXiv and translate via the digest skill.

    Runs outside the event loop (called via asyncio.to_thread). Fetches directly
    (bypassing the digest's seen_papers dedup) so the papers table can be
    populated/refreshed regardless of what the daily cron already delivered.
    """
    scripts = _digest_scripts_dir()
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from datetime import datetime, timedelta
    from arxiv_fetcher import fetch_papers
    from translate import translate_papers
    from digest import load_config

    config = load_config(settings.arxiv_digest_dir) or {}
    categories = config.get("categories") or ["cs.IT", "eess.SP"]

    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")
    papers = fetch_papers(categories, max_results=max_papers, date_from=date_from, date_to=date_to)

    if isinstance(papers, dict) and "error" in papers:
        return {"fetched": 0, "papers": [], "error": papers["error"]}
    if not papers:
        return {"fetched": 0, "papers": [], "error": None}

    cfg = {"translate": {
        "base_url": settings.openclaw_base_url,
        "api_key": settings.openclaw_api_key,
        "model": settings.openclaw_model,
    }}
    processed = translate_papers({"papers": papers}, config=cfg)
    return {"fetched": len(papers), "papers": processed.get("papers", []), "error": None}


async def refresh_papers(db: AsyncSession, days: int = 7, max_papers: int = 20) -> dict:
    """Fetch latest papers, translate, and upsert into the database."""
    result = await asyncio.to_thread(_sync_fetch_and_translate, days, max_papers)

    new = updated = 0
    for p in result.get("papers", []):
        if not p.get("arxiv_id"):
            continue
        existing = await db.execute(select(Paper).where(Paper.arxiv_id == p["arxiv_id"]))
        obj = existing.scalar_one_or_none()
        data = {
            "title": p.get("title", ""),
            "title_zh": p.get("title_zh") or None,
            "authors": p.get("authors") or [],
            "abstract": p.get("abstract", ""),
            "abstract_zh": p.get("abstract_zh") or None,
            "keywords": p.get("keywords") or [],
            "primary_category": p.get("primary_category"),
            "categories": p.get("categories") or [],
            "published": p.get("published"),
            "updated": p.get("updated"),
            "link": p.get("link"),
        }
        if obj is None:
            db.add(Paper(arxiv_id=p["arxiv_id"], **data))
            new += 1
        else:
            for k, v in data.items():
                setattr(obj, k, v)
            updated += 1
    await db.commit()
    return {"fetched": result["fetched"], "new": new, "updated": updated, "error": result.get("error")}


def build_author_prompt(paper: Paper) -> str:
    """Build the virtual-author system prompt for one-on-one Q&A."""
    authors = paper.authors or []
    first_author = authors[0] if authors else "the first author"
    author_list = ", ".join(authors[:5]) + (" et al." if len(authors) > 5 else "")
    zh = f"\n- Chinese abstract: {paper.abstract_zh}" if paper.abstract_zh else ""
    return (
        f"You are {first_author}, the first author of the paper \"{paper.title}\" "
        f"(arXiv: {paper.arxiv_id}).\n\n"
        f"You are being interviewed one-on-one about this paper. Answer in first "
        f"person, as the paper's author, explaining your motivation, method, and results.\n\n"
        f"Paper metadata:\n"
        f"- Title: {paper.title}\n"
        f"- Authors: {author_list}\n"
        f"- Published: {paper.published or 'unknown'}\n"
        f"- Category: {paper.primary_category or 'unknown'}\n"
        f"- Abstract: {paper.abstract}\n"
        f"{zh}\n\n"
        f"Ground your answers in the paper's abstract. If asked about details not in "
        f"the abstract, say so honestly rather than fabricating. Reply in the same "
        f"language as the user."
    )
