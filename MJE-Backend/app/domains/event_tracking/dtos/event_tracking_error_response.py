from __future__ import annotations

from pydantic import BaseModel

from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingDuplicateEventError,
    EventTrackingPersistenceError,
)


class EventTrackingErrorResponse(BaseModel):
    code: str
    message: str
    field: str | None = None
    invalid_value: str | None = None
    session_id: str | None = None
    attempt_id: str | None = None
    event_type: str | None = None


def from_duplicate_event_error(
    error: EventTrackingDuplicateEventError,
) -> EventTrackingErrorResponse:
    """HTTP 응답용: 중복 저장 등 충돌(SC: 동일 시도 1회)."""
    return EventTrackingErrorResponse(
        code=error.error_code,
        message=str(error),
        field="attempt_id",
        invalid_value=error.attempt_id,
        session_id=error.session_id,
        attempt_id=error.attempt_id,
    )


def from_persistence_error(
    error: EventTrackingPersistenceError,
) -> EventTrackingErrorResponse:
    """HTTP 응답용: 저장 실패(일시적 DB 오류 등)."""
    return EventTrackingErrorResponse(
        code=error.error_code,
        message=str(error),
        session_id=error.session_id,
        event_type=error.event_type,
    )
