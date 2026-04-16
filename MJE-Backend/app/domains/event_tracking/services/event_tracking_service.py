import re
from uuid import uuid4

from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.dtos.event_response import EventResponse
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
)


class EventTrackingService:
    """Use-case orchestration for event tracking domain."""

    _SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{5,127}$")

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

        return EventResponse(
            event_id=str(uuid4()),
            status="accepted",
        )
