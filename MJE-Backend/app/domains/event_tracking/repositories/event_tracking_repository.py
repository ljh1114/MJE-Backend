from __future__ import annotations

from abc import ABC, abstractmethod

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


class EventTrackingRepository(ABC):
    """Persistence port for tracking events."""

    @abstractmethod
    def save(self, event: TrackingEvent) -> None:
        raise NotImplementedError


class NullEventTrackingRepository(EventTrackingRepository):
    """No-op persistence when database_url is not configured."""

    def save(self, event: TrackingEvent) -> None:
        return None


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
