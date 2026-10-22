#!/usr/bin/env python3.11
"""Daily cron: refresh the papers table with latest arXiv papers (答疑模块自动更新).

Replaces the old arxiv-wireless-digest schedule_runner cron. Runs the FastAPI
app's refresh_papers() directly (no HTTP, no auth) against the same .env and
SQLite db the app uses, so 答疑's 论文库 gets fresh papers every day.
"""
import asyncio
import os
import sys

BACKEND_DIR = "/opt/wireless-agent/backend"
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

from app.database import async_session
from app.services.paper_service import refresh_papers


async def main():
    async with async_session() as db:
        result = await refresh_papers(db, days=1, max_papers=20)
        print(result)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"refresh_papers_daily failed: {exc}")
        sys.exit(1)
