from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, JSON, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TrackingEventRow(Base):
    """ORM row for tracking_events (PostgreSQL JSONB / SQLite JSON).

    탐색 성과(MJE-BE-9)
    - 시작·저장 클릭은 ``event_type`` + ``event_payload`` 로 구분한다.
    - ``attempt_id`` 컬럼은 시도 단위 조회·중복(저장 1회) 제약을 위해 정규화한다.
    - 실패 전용 행은 두지 않는다(SC: 생성 대비 저장 부재로 판단).
    """

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
        Index(
            "ix_tracking_events_session_id_attempt_id",
            "session_id",
            "attempt_id",
        ),
        Index(
            "uq_tracking_events_save_click_once_per_attempt",
            "session_id",
            "attempt_id",
            unique=True,
            postgresql_where=text(
                "event_type = 'save_course_clicked' AND attempt_id IS NOT NULL"
            ),
            sqlite_where=text(
                "event_type = 'save_course_clicked' AND attempt_id IS NOT NULL"
            ),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    attempt_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    event_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
