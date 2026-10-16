"""Shared dependencies: unified ownership/permission check."""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


async def get_owned(db: AsyncSession, model, resource_id: str, user_id: str, not_found: str = "资源不存在"):
    """Fetch a user-owned resource or raise 404 (same error for missing or foreign)."""
    obj = await db.get(model, resource_id)
    if obj is None or getattr(obj, "user_id", None) != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found)
    return obj