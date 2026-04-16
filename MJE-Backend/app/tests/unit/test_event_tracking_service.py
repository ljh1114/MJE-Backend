from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.services.event_tracking_service import (
    EventTrackingService,
)


def test_collect_event_returns_accepted_response() -> None:
    service = EventTrackingService()

    response = service.collect_event(
        EventRequest(
            event_type="create_course_clicked",
            session_id="session-123",
        )
    )

    assert response.status == "accepted"
    assert response.event_id
