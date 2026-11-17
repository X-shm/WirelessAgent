"""记忆模块：长期记忆读写（纯数据层，不依赖工具注册表）。"""
from sqlalchemy import select

from app.database import async_session
from app.models.memory import Memory


class MemoryStore:
    async def add(self, user_id: str, key: str, content: str, importance: int = 0) -> dict:
        async with async_session() as db:
            mem = Memory(user_id=user_id, key=key, content=content, importance=importance)
            db.add(mem)
            await db.commit()
            await db.refresh(mem)
            return {"id": mem.id, "key": mem.key, "content": mem.content, "importance": mem.importance}

    async def list(self, user_id: str, top_k: int = 10) -> list[dict]:
        async with async_session() as db:
            rows = (
                await db.execute(
                    select(Memory)
                    .where(Memory.user_id == user_id)
                    .order_by(Memory.importance.desc(), Memory.updated_at.desc())
                    .limit(top_k)
                )
            ).scalars().all()
            return [{"key": m.key, "content": m.content, "importance": m.importance} for m in rows]

    @staticmethod
    def to_prompt(memories: list[dict]) -> str:
        if not memories:
            return ""
        lines = ["## 用户长期记忆（此前已记住的偏好 / 事实）"]
        for m in memories:
            lines.append(f"- {m['key']}: {m['content']}")
        return "\n".join(lines)


memory_store = MemoryStore()
