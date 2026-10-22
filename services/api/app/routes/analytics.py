"""Analytics routes — CSV export for teacher analysis."""
import io, csv
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.analytics import Analytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/export", response_model=None)
async def export_csv(db: AsyncSession = Depends(get_db)):
    """Export all analytics data as CSV."""
    result = await db.execute(select(Analytics).order_by(Analytics.timestamp.desc()))
    rows = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "session_id", "user_id", "question", "answer", "timestamp"])
    for r in rows:
        writer.writerow([r.id, r.session_id, r.user_id, r.question, r.answer, r.timestamp.isoformat()])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics_export.csv"}
    )
