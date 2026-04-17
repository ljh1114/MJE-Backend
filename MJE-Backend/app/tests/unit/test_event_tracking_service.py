from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
)
from app.domains.event_tracking.repositories.event_tracking_repository import (
    EventTrackingRepository,
    NullEventTrackingRepository,
)
from app.domains.event_tracking.services.event_tracking_service import (
    EventTrackingService,
)


class RecordingEventTrackingRepository(EventTrackingRepository):
    def __init__(self) -> None:
        self.saved: list[TrackingEvent] = []

    def save(self, event: TrackingEvent) -> None:
        self.saved.append(event)

    def find_by_session_id(self, session_id: str) -> list[TrackingEvent]:
        return sorted(
            (e for e in self.saved if e.session_id == session_id),
            key=lambda e: e.occurred_at,
        )


def test_collect_event_returns_accepted_response() -> None:
    service = EventTrackingService(NullEventTrackingRepository())

    response = service.collect_event(
        EventRequest(
            event_type="create_course_clicked",
            session_id="sess_01HZ",
            page_url="https://example.com/planner",
        )
    )

    assert response.status == "accepted"
    assert response.event_id


def test_collect_event_delegates_to_repository() -> None:
    repository = RecordingEventTrackingRepository()
    service = EventTrackingService(repository)

    response = service.collect_event(
        EventRequest(
            event_type="date_course_explore_clicked",
            session_id="sess_01HZ",
            page_url="https://example.com/explore",
        )
    )

    assert len(repository.saved) == 1
    saved = repository.saved[0]
    assert saved.event_type == "date_course_explore_clicked"
    assert saved.event_payload["page_url"] == "https://example.com/explore"
    assert str(saved.id) == response.event_id


def test_collect_event_rejects_invalid_session_id() -> None:
    service = EventTrackingService(NullEventTrackingRepository())

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
