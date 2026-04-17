from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingPersistenceError,
)
from app.domains.event_tracking.repositories.tracking_event_row import (
    TrackingEventRow,
)


def _row_to_entity(row: TrackingEventRow) -> TrackingEvent:
    return TrackingEvent(
        id=UUID(row.id),
        session_id=row.session_id,
        user_id=row.user_id,
        event_type=row.event_type,
        event_payload=dict(row.event_payload),
        occurred_at=row.occurred_at,
    )


class EventTrackingRepository(ABC):
    """Persistence port for tracking events."""

    @abstractmethod
    def save(self, event: TrackingEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_session_id(self, session_id: str) -> list[TrackingEvent]:
        """세션에 속한 이벤트를 발생 시각 순으로 반환."""
        raise NotImplementedError


class NullEventTrackingRepository(EventTrackingRepository):
    """No-op persistence when database_url is not configured."""

    def save(self, event: TrackingEvent) -> None:
        return None

    def find_by_session_id(self, session_id: str) -> list[TrackingEvent]:
        return []


class SqlAlchemyEventTrackingRepository(EventTrackingRepository):
    """SQLAlchemy-backed persistence for tracking_events."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, event: TrackingEvent) -> None:
        row = TrackingEventRow(
            id=str(event.id),
            session_id=event.session_id,
            user_id=event.user_id,
            event_type=event.event_type,
            event_payload=dict(event.event_payload),
            occurred_at=event.occurred_at,
        )
        try:
            with Session(self._engine) as session:
                session.add(row)
                session.commit()
        except SQLAlchemyError as exc:
            raise EventTrackingPersistenceError() from exc

    def find_by_session_id(self, session_id: str) -> list[TrackingEvent]:
        stmt = (
            select(TrackingEventRow)
            .where(TrackingEventRow.session_id == session_id)
            .order_by(TrackingEventRow.occurred_at.asc())
        )
        try:
            with Session(self._engine) as session:
                rows = session.scalars(stmt).all()
        except SQLAlchemyError as exc:
            raise EventTrackingPersistenceError() from exc
        return [_row_to_entity(r) for r in rows]
