from fastapi import APIRouter, status

from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.dtos.event_response import EventResponse
from app.domains.event_tracking.dtos.event_tracking_error_response import (
    EventTrackingErrorResponse,
)
from app.domains.event_tracking.services.event_tracking_service import (
    EventTrackingService,
)

router = APIRouter(prefix="/api/v1/events", tags=["event_tracking"])
event_tracking_service = EventTrackingService()


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={400: {"model": EventTrackingErrorResponse}},
)
def collect_event(
    request: EventRequest,
) -> EventResponse:
    return event_tracking_service.collect_event(request)
