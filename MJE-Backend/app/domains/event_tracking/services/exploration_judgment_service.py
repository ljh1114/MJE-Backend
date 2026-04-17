import re

from app.domains.event_tracking.entities.session_exploration_result import (
    SessionExplorationSummary,
)
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
)
from app.domains.event_tracking.exploration_judgment import judge_session_exploration
from app.domains.event_tracking.repositories.event_tracking_repository import (
    EventTrackingRepository,
)


class ExplorationJudgmentService:
    """세션 단위 탐색 성과 판단 유스케이스."""

    _SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{5,127}$")

    def __init__(self, repository: EventTrackingRepository) -> None:
        self._repository = repository

    def evaluate_session(self, session_id: str) -> SessionExplorationSummary:
        raw = session_id.strip()
        if not self._SESSION_ID_PATTERN.fullmatch(raw):
            raise EventTrackingInvalidInputError(
                field_name="session_id",
                field_value=session_id,
                message=(
                    "session_id must be 6-128 characters and may contain letters, "
                    "digits, '.', '_', or '-' (must start with a letter or digit)."
                ),
            )

        events = self._repository.find_by_session_id(raw)
        attempts = judge_session_exploration(events)
        return SessionExplorationSummary(session_id=raw, attempts=tuple(attempts))
