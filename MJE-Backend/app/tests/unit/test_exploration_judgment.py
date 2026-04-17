from datetime import datetime, timezone
from uuid import uuid4

from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exploration_criteria import (
    ATTEMPT_ID_PAYLOAD_KEY,
    EXPLORATION_SAVE_CLICK_EVENT_TYPE,
    EXPLORATION_START_EVENT_TYPE,
    ExplorationOutcome,
)
from app.domains.event_tracking.exploration_judgment import (
    classify_exploration_attempt,
    extract_attempt_id_from_payload,
    judge_outcome_for_attempt,
)


def test_classify_success_when_start_and_save() -> None:
    assert (
        classify_exploration_attempt(
            has_start_event=True,
            has_save_click_event=True,
        )
        == ExplorationOutcome.SUCCESS
    )


def test_classify_not_completed_when_start_only() -> None:
    assert (
        classify_exploration_attempt(
            has_start_event=True,
            has_save_click_event=False,
        )
        == ExplorationOutcome.NOT_COMPLETED
    )


def test_classify_none_when_no_start() -> None:
    assert (
        classify_exploration_attempt(
            has_start_event=False,
            has_save_click_event=True,
        )
        is None
    )
    assert (
        classify_exploration_attempt(
            has_start_event=False,
            has_save_click_event=False,
        )
        is None
    )


def test_judge_outcome_for_attempt_matches_by_attempt_id() -> None:
    attempt = "att_01HZ"
    base = "sess_x"
    t0 = datetime.now(timezone.utc)
    events = [
        TrackingEvent(
            id=uuid4(),
            session_id=base,
            user_id=None,
            event_type=EXPLORATION_START_EVENT_TYPE,
            event_payload={
                "page_url": "https://example.com/p",
                ATTEMPT_ID_PAYLOAD_KEY: attempt,
            },
            occurred_at=t0,
        ),
        TrackingEvent(
            id=uuid4(),
            session_id=base,
            user_id=None,
            event_type=EXPLORATION_SAVE_CLICK_EVENT_TYPE,
            event_payload={
                "page_url": "https://example.com/p",
                ATTEMPT_ID_PAYLOAD_KEY: attempt,
            },
            occurred_at=t0,
        ),
    ]
    assert judge_outcome_for_attempt(events, attempt_id=attempt) == ExplorationOutcome.SUCCESS


def test_judge_outcome_not_completed_without_save() -> None:
    attempt = "att_02HZ"
    events = [
        TrackingEvent(
            id=uuid4(),
            session_id="sess_x",
            user_id=None,
            event_type=EXPLORATION_START_EVENT_TYPE,
            event_payload={
                "page_url": "https://example.com/p",
                ATTEMPT_ID_PAYLOAD_KEY: attempt,
            },
            occurred_at=datetime.now(timezone.utc),
        ),
    ]
    assert (
        judge_outcome_for_attempt(events, attempt_id=attempt)
        == ExplorationOutcome.NOT_COMPLETED
    )


def test_extract_attempt_id_from_payload() -> None:
    assert extract_attempt_id_from_payload({ATTEMPT_ID_PAYLOAD_KEY: "  x  "}) == "x"
    assert extract_attempt_id_from_payload({}) is None
