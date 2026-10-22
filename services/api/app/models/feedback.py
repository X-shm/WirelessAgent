"""Feedback model."""
from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, utcnow, new_uuid
from datetime import datetime


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
