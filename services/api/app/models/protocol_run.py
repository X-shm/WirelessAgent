"""Private, resumable state for a standard-search request."""

from datetime import datetime

from sqlalchemy import JSON, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utcnow


class ProtocolRun(Base):
    __tablename__ = "protocol_runs"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    inputs: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(24), default="queued")
    stage: Mapped[str] = mapped_column(String(24), default="prepare")
    in_flight: Mapped[bool] = mapped_column(default=False)
    attempts: Mapped[dict] = mapped_column(JSON, default=dict)
    error_kind: Mapped[str | None] = mapped_column(String(24))
    lease: Mapped[str | None] = mapped_column(String(36))
    lease_until: Mapped[datetime | None] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    purged_at: Mapped[datetime | None] = mapped_column()
    attempt: Mapped[int] = mapped_column(default=0)
    last_seq: Mapped[int] = mapped_column(default=0)
    message_id: Mapped[str | None] = mapped_column(String(36))


class ProtocolCheckpoint(Base):
    __tablename__ = "protocol_checkpoints"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    stage: Mapped[str] = mapped_column(String(24), primary_key=True)
    payload: Mapped[dict | list | None] = mapped_column(JSON)
    binary: Mapped[bytes | None] = mapped_column(LargeBinary)


class ProtocolEvent(Base):
    __tablename__ = "protocol_events"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    seq: Mapped[int] = mapped_column(primary_key=True)
    attempt: Mapped[int] = mapped_column()
    token: Mapped[str | None] = mapped_column(Text)
