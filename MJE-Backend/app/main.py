from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domains.recommendation.dtos.recommendation_error_response import (
    RecommendationErrorResponse,
)
from app.domains.saved_course.dtos.saved_course_error_response import (
    SavedCourseErrorResponse,
)
from app.domains.event_tracking.dtos.event_tracking_error_response import (
    EventTrackingErrorResponse,
)
from app.domains.recommendation.controllers.recommendation_controller import router as recommendation_router
from app.domains.saved_course.controllers.saved_course_controller import (
    router as saved_course_router,
)
from app.domains.event_tracking.controllers.event_tracking_controller import (
    router as event_tracking_router,
)


def create_app() -> FastAPI:
    app = FastAPI(title="MJE Backend", version="0.1.0")

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        if request.url.path.startswith("/api/v1/events"):
            first_error = exc.errors()[0]
            if first_error.get("type") == "json_invalid":
                error_response = EventTrackingErrorResponse(
                    code="EVENT_TRACKING_INVALID_REQUEST",
                    message="Event tracking request body is not valid JSON.",
                    field="body",
                    invalid_value=None,
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_response.model_dump(),
                )

            field_name = (
                first_error["loc"][-1] if first_error.get("loc") else None
            )
            if isinstance(field_name, int):
                field_name = "body"
            invalid_value = None
            if isinstance(first_error.get("input"), (str, int, float, bool)):
                invalid_value = str(first_error["input"])

            error_response = EventTrackingErrorResponse(
                code="EVENT_TRACKING_INVALID_REQUEST",
                message="Event tracking request payload is invalid.",
                field=str(field_name) if field_name is not None else None,
                invalid_value=invalid_value,
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response.model_dump(),
            )

        if request.url.path.startswith("/api/v1/saved-courses"):
            first_error = exc.errors()[0]
            field_name = (
                first_error["loc"][-1] if first_error.get("loc") else None
            )
            invalid_value = None
            if isinstance(first_error.get("input"), (str, int, float, bool)):
                invalid_value = str(first_error["input"])

            error_response = SavedCourseErrorResponse(
                code="SAVED_COURSE_INVALID_REQUEST",
                message="Saved course request payload is invalid.",
                field=str(field_name) if field_name is not None else None,
                invalid_value=invalid_value,
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response.model_dump(),
            )

        if not request.url.path.startswith("/api/v1/recommendations"):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": exc.errors()},
            )

        first_error = exc.errors()[0]
        field_name = (
            first_error["loc"][-1] if first_error.get("loc") else None
        )
        invalid_value = None
        if isinstance(first_error.get("input"), (str, int, float, bool)):
            invalid_value = str(first_error["input"])

        error_response = RecommendationErrorResponse(
            code="RECOMMENDATION_INVALID_REQUEST",
            message="Recommendation request payload is invalid.",
            field=str(field_name) if field_name is not None else None,
            invalid_value=invalid_value,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump(),
        )

    app.include_router(recommendation_router)
    app.include_router(saved_course_router)
    app.include_router(event_tracking_router)
    return app


app = create_app()
