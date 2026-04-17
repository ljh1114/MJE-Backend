"""세션 단위 탐색 성과 판단 결과 (집계용 도메인 모델)."""

from __future__ import annotations

from dataclasses import dataclass

from app.domains.event_tracking.exploration_criteria import ExplorationOutcome


@dataclass(frozen=True, slots=True)
class SessionExplorationAttemptResult:
    """한 세션 안의 단일 탐색 시도(attempt_id)에 대한 판단."""

    attempt_id: str
    # None: 탐색 시작 이벤트가 없어 판단 불가(저장만 들어온 비정상 케이스 등).
    outcome: ExplorationOutcome | None


@dataclass(frozen=True, slots=True)
class SessionExplorationSummary:
    """세션별 탐색 성과 판단 결과."""

    session_id: str
    attempts: tuple[SessionExplorationAttemptResult, ...]
