from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
)
from app.domains.event_tracking.services.event_tracking_service import (
    EventTrackingService,
)


def test_collect_event_returns_accepted_response() -> None:
    service = EventTrackingService()

    response = service.collect_event(
        EventRequest(
            event_type="create_course_clicked",
            session_id="sess_01HZ",
            page_url="https://example.com/planner",
        )
    )

    assert response.status == "accepted"
    assert response.event_id


def test_collect_event_rejects_invalid_session_id() -> None:
    service = EventTrackingService()

    try:
        service.collect_event(
            EventRequest(
                event_type="create_course_clicked",
                session_id="bad",
                page_url="https://example.com/planner",
            )
        )
    except EventTrackingInvalidInputError as error:
        assert error.field_name == "session_id"
    else:
        raise AssertionError("Expected EventTrackingInvalidInputError")
