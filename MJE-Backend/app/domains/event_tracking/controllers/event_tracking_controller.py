from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.event_tracking.dtos.event_request import EventRequest
from app.domains.event_tracking.dtos.event_response import EventResponse
from app.domains.event_tracking.dtos.event_tracking_error_response import (
    EventTrackingErrorResponse,
)
from app.domains.event_tracking.event_tracking_dependencies import (
    get_event_tracking_service,
)
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingInvalidInputError,
    EventTrackingPersistenceError,
)
from app.domains.event_tracking.services.event_tracking_service import (
    EventTrackingService,
)

router = APIRouter(prefix="/api/v1/events", tags=["event_tracking"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": EventTrackingErrorResponse},
        503: {"model": EventTrackingErrorResponse},
    },
)
def collect_event(
    request: EventRequest,
    event_tracking_service: EventTrackingService = Depends(get_event_tracking_service),
) -> EventResponse:
    try:
        return event_tracking_service.collect_event(request)
    except EventTrackingInvalidInputError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=EventTrackingErrorResponse(
                code=error.error_code,
                message=str(error),
                field=error.field_name,
                invalid_value=error.field_value,
            ).model_dump(),
        ) from error
    except EventTrackingPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=EventTrackingErrorResponse(
                code=error.error_code,
                message=str(error),
            ).model_dump(),
        ) from error
