"""Analytics model — record Q&A for teacher export."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.models.base import Base
import uuid
from datetime import datetime

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
