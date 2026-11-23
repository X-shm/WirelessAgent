"""One persisted record for each request made through standard search."""

from datetime import datetime

from sqlalchemy import CheckConstraint, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid, utcnow


class ProtocolSearchLog(Base):
    __tablename__ = "protocol_search_logs"
    __table_args__ = (CheckConstraint(
        "status IN ('running', 'complete', 'search_failed', 'generation_interrupted')",
        name="ck_protocol_search_logs_status",
    ),)

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    question: Mapped[str] = mapped_column(Text)
    query: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="running")
    retrieval: Mapped[dict] = mapped_column(JSON, default=dict)
    answer: Mapped[str] = mapped_column(Text, default="")
    citations: Mapped[list] = mapped_column(JSON, default=list)
