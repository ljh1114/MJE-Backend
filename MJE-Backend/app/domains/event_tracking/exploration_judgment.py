"""탐색 성과 판단 (순수 함수). Repository·HTTP에 의존하지 않는다."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exploration_criteria import (
    ATTEMPT_ID_PAYLOAD_KEY,
    EXPLORATION_SAVE_CLICK_EVENT_TYPE,
    EXPLORATION_START_EVENT_TYPE,
    ExplorationOutcome,
)


def classify_exploration_attempt(
    *,
    has_start_event: bool,
    has_save_click_event: bool,
) -> ExplorationOutcome | None:
    """단일 탐색 시도에 대해 시작·저장 클릭 존재 여부만으로 결과를 낸다.

    - 시작 이벤트가 없으면 ``None`` (판단 대상 아님).
    - 시작만 있고 저장 클릭이 없으면 ``NOT_COMPLETED`` (실패, 별도 실패 이벤트 없음).
    - 시작과 저장 클릭이 모두 있으면 ``SUCCESS``.
    """
    if not has_start_event:
        return None
    if has_save_click_event:
        return ExplorationOutcome.SUCCESS
    return ExplorationOutcome.NOT_COMPLETED


def _payload_attempt_id(event: TrackingEvent) -> str | None:
    raw = event.event_payload.get(ATTEMPT_ID_PAYLOAD_KEY)
    if raw is None:
        return None
    if isinstance(raw, str):
        s = raw.strip()
        return s if s else None
    return str(raw)


def judge_outcome_for_attempt(
    events: Sequence[TrackingEvent],
    *,
    attempt_id: str,
) -> ExplorationOutcome | None:
    """같은 ``attempt_id``를 가진 이벤트들만 모아 한 시도의 성과를 판단한다.

    ``attempt_id``가 없는 과거 이벤트만 있는 경우, 시도 단위 판단은 할 수 없다
    (``classify_exploration_attempt``를 플래그로 호출하는 쪽에서 처리).
    """
    aid = attempt_id.strip()
    if not aid:
        return None

    matching: list[TrackingEvent] = []
    for e in events:
        if _payload_attempt_id(e) != aid:
            continue
        matching.append(e)

    has_start = any(e.event_type == EXPLORATION_START_EVENT_TYPE for e in matching)
    has_save = any(e.event_type == EXPLORATION_SAVE_CLICK_EVENT_TYPE for e in matching)
    return classify_exploration_attempt(
        has_start_event=has_start,
        has_save_click_event=has_save,
    )


def extract_attempt_id_from_payload(payload: dict[str, Any]) -> str | None:
    """요청/페이로드에서 attempt_id를 꺼낸다 (검증은 상위에서)."""
    raw = payload.get(ATTEMPT_ID_PAYLOAD_KEY)
    if raw is None:
        return None
    if isinstance(raw, str):
        s = raw.strip()
        return s if s else None
    return str(raw)
