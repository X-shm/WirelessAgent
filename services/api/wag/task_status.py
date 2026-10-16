"""Unified task status and transition rules."""
import enum
from fastapi import HTTPException


class TaskStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


ALLOWED_TRANSITIONS = {
    TaskStatus.pending: {TaskStatus.queued, TaskStatus.cancelled},
    TaskStatus.queued: {TaskStatus.running, TaskStatus.cancelled},
    TaskStatus.running: {TaskStatus.succeeded, TaskStatus.failed, TaskStatus.cancelled},
    TaskStatus.succeeded: set(),
    TaskStatus.failed: set(),
    TaskStatus.cancelled: set(),
}

TERMINAL = {TaskStatus.succeeded, TaskStatus.failed, TaskStatus.cancelled}


def ensure_transition(current: str, new: str) -> TaskStatus:
    """Validate a status transition; raise 409 on invalid move."""
    cur = TaskStatus(current)
    nxt = TaskStatus(new)
    if cur == nxt:
        return nxt
    if nxt not in ALLOWED_TRANSITIONS.get(cur, set()):
        raise HTTPException(status_code=409, detail=f"Invalid task status transition: {current} -> {new}")
    return nxt