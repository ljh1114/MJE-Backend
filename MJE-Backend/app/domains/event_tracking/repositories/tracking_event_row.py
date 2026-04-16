from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TrackingEventRow(Base):
    """ORM row for tracking_events (PostgreSQL JSONB / SQLite JSON)."""

    __tablename__ = "tracking_events"
    __table_args__ = (
        Index(
            "ix_tracking_events_event_type_occurred_at",
            "event_type",
            "occurred_at",
        ),
        Index(
            "ix_tracking_events_session_occurred_at",
            "session_id",
            "occurred_at",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
