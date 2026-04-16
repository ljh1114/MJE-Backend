from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TrackingEvent:
    """Domain record for a single tracked client event (PRD 10.3)."""

    id: UUID
    session_id: str
    user_id: str | None
    event_type: str
    event_payload: dict[str, Any]
    occurred_at: datetime
