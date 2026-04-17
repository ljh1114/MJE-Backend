import re
from datetime import datetime, timezone
from uuid import uuid4

from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.dtos.event_response import EventResponse
from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
)
from app.domains.event_tracking.exploration_criteria import (
    ATTEMPT_ID_PAYLOAD_KEY,
    DATE_COURSE_EXPLORE_CLICKED_EVENT_TYPE,
    EXPLORATION_SAVE_CLICK_EVENT_TYPE,
    EXPLORATION_START_EVENT_TYPE,
)
from app.domains.event_tracking.repositories.event_tracking_repository import (
    EventTrackingRepository,
)

_EXPLORATION_FLOW_EVENTS = frozenset(
    {
        EXPLORATION_START_EVENT_TYPE,
        EXPLORATION_SAVE_CLICK_EVENT_TYPE,
    }
)


class EventTrackingService:
    """Use-case orchestration for event tracking domain."""

    _SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{5,127}$")
    _ATTEMPT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{5,127}$")

    def __init__(self, repository: EventTrackingRepository) -> None:
        self._repository = repository

    def collect_event(self, request: EventRequest) -> EventResponse:
        session_id = request.session_id.strip()
        if not self._SESSION_ID_PATTERN.fullmatch(session_id):
            raise EventTrackingInvalidInputError(
                field_name="session_id",
                field_value=request.session_id,
                message=(
                    "session_id must be 6-128 characters and may contain letters, "
                    "digits, '.', '_', or '-' (must start with a letter or digit)."
                ),
            )

        page_url = str(request.page_url).strip()
        scheme = str(request.page_url.scheme).lower()
        if scheme not in {"http", "https"}:
            raise EventTrackingInvalidInputError(
                field_name="page_url",
                field_value=page_url,
                message="page_url must use http or https.",
            )

        attempt_id: str | None
        event_payload: dict[str, str]

        if request.event_type in _EXPLORATION_FLOW_EVENTS:
            raw_attempt = request.attempt_id
            if raw_attempt is None or not str(raw_attempt).strip():
                raise EventTrackingInvalidInputError(
                    field_name="attempt_id",
                    field_value=raw_attempt or "",
                    message=(
                        "attempt_id is required for create_course_clicked and "
                        "save_course_clicked."
                    ),
                )
            aid = str(raw_attempt).strip()
            if not self._ATTEMPT_ID_PATTERN.fullmatch(aid):
                raise EventTrackingInvalidInputError(
                    field_name="attempt_id",
                    field_value=aid,
                    message=(
                        "attempt_id must be 6-128 characters and may contain letters, "
                        "digits, '.', '_', or '-' (must start with a letter or digit)."
                    ),
                )
            attempt_id = aid
            event_payload = {
                "page_url": page_url,
                ATTEMPT_ID_PAYLOAD_KEY: aid,
            }
        else:
            if request.event_type == DATE_COURSE_EXPLORE_CLICKED_EVENT_TYPE:
                if request.attempt_id is not None and str(request.attempt_id).strip():
                    raise EventTrackingInvalidInputError(
                        field_name="attempt_id",
                        field_value=str(request.attempt_id).strip(),
                        message="attempt_id must not be sent for date_course_explore_clicked.",
                    )
            attempt_id = None
            event_payload = {"page_url": page_url}

        event_id = uuid4()
        event = TrackingEvent(
            id=event_id,
            session_id=session_id,
            user_id=None,
            event_type=request.event_type,
            event_payload=event_payload,
            occurred_at=datetime.now(timezone.utc),
            attempt_id=attempt_id,
        )
        self._repository.save(event)

        return EventResponse(
            event_id=str(event_id),
            status="accepted",
        )
