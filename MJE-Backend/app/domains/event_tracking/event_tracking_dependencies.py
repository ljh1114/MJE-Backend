from fastapi import Depends

from app.core.config import settings
from app.core.database import get_engine
from app.domains.event_tracking.repositories.event_tracking_repository import (
    EventTrackingRepository,
    NullEventTrackingRepository,
    SqlAlchemyEventTrackingRepository,
)
from app.domains.event_tracking.services.event_tracking_service import (
    EventTrackingService,
)


def get_event_tracking_repository() -> EventTrackingRepository:
    if not settings.database_url:
        return NullEventTrackingRepository()
    return SqlAlchemyEventTrackingRepository(get_engine())


def get_event_tracking_service(
    repository: EventTrackingRepository = Depends(get_event_tracking_repository),
) -> EventTrackingService:
    return EventTrackingService(repository)
