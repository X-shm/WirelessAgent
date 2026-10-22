"""Paper model — persisted arXiv papers for Agent2Paper."""
from datetime import datetime
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, utcnow, new_uuid


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    arxiv_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    title_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    abstract: Mapped[str] = mapped_column(Text, nullable=False, default="")
    abstract_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    primary_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    categories: Mapped[list | None] = mapped_column(JSON, nullable=True)
    published: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated: Mapped[str | None] = mapped_column(String(32), nullable=True)
    link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
