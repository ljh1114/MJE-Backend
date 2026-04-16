from uuid import uuid4

from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.dtos.event_response import EventResponse


class EventTrackingService:
    """Use-case orchestration for event tracking domain."""

    def collect_event(self, request: EventRequest) -> EventResponse:
        return EventResponse(
            event_id=str(uuid4()),
            status="accepted",
        )
