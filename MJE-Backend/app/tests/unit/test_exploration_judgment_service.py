from datetime import datetime, timezone
from uuid import uuid4

from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
)
from app.domains.event_tracking.exploration_criteria import (
    ATTEMPT_ID_PAYLOAD_KEY,
    EXPLORATION_SAVE_CLICK_EVENT_TYPE,
    EXPLORATION_START_EVENT_TYPE,
    ExplorationOutcome,
)
from app.domains.event_tracking.repositories.event_tracking_repository import (
    EventTrackingRepository,
)
from app.domains.event_tracking.services.exploration_judgment_service import (
    ExplorationJudgmentService,
)


class _MemoryRepo(EventTrackingRepository):
    def __init__(self, events: list[TrackingEvent]) -> None:
        self._events = events

    def save(self, event: TrackingEvent) -> None:
        self._events.append(event)

    def find_by_session_id(self, session_id: str) -> list[TrackingEvent]:
        return sorted(
            (e for e in self._events if e.session_id == session_id),
            key=lambda e: e.occurred_at,
        )


def test_evaluate_session_returns_summary() -> None:
    sid = "sess_01HZ"
    t0 = datetime.now(timezone.utc)
    events = [
        TrackingEvent(
            id=uuid4(),
            session_id=sid,
            user_id=None,
            event_type=EXPLORATION_START_EVENT_TYPE,
            event_payload={
                "page_url": "https://example.com/p",
                ATTEMPT_ID_PAYLOAD_KEY: "att1",
            },
            occurred_at=t0,
        ),
        TrackingEvent(
            id=uuid4(),
            session_id=sid,
            user_id=None,
            event_type=EXPLORATION_SAVE_CLICK_EVENT_TYPE,
            event_payload={
                "page_url": "https://example.com/p",
                ATTEMPT_ID_PAYLOAD_KEY: "att1",
            },
            occurred_at=t0,
        ),
    ]
    service = ExplorationJudgmentService(_MemoryRepo(events))
    summary = service.evaluate_session(sid)
    assert summary.session_id == sid
    assert len(summary.attempts) == 1
    assert summary.attempts[0].attempt_id == "att1"
    assert summary.attempts[0].outcome == ExplorationOutcome.SUCCESS


def test_evaluate_session_rejects_invalid_session_id() -> None:
    service = ExplorationJudgmentService(_MemoryRepo([]))
    try:
        service.evaluate_session("bad")
    except EventTrackingInvalidInputError as e:
        assert e.field_name == "session_id"
    else:
        raise AssertionError("expected EventTrackingInvalidInputError")
