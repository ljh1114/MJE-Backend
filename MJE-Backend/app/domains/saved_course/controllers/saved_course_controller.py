from fastapi import APIRouter, Response, status

from app.domains.saved_course.dtos.send_saved_course_email_request import (
    SendSavedCourseEmailRequest,
)
from app.domains.saved_course.dtos.send_saved_course_email_response import (
    SendSavedCourseEmailResponse,
)
from app.domains.saved_course.dtos.saved_course_error_response import (
    SavedCourseErrorResponse,
)
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationCourseIdentifierError,
    RecommendationCourseIdentifierFormatError,
    RecommendationInvalidCourseResultError,
)
from app.domains.saved_course.services.saved_course_service import SavedCourseService

router = APIRouter(prefix="/api/v1/saved-courses", tags=["saved_course"])
saved_course_service = SavedCourseService()


@router.post(
    "/email",
    response_model=SendSavedCourseEmailResponse,
    status_code=status.HTTP_200_OK,
    responses={400: {"model": SavedCourseErrorResponse}},
)
def send_saved_course_email(
    request: SendSavedCourseEmailRequest,
    response: Response,
) -> SendSavedCourseEmailResponse:
    try:
        result = saved_course_service.create_email_send_request(request)
    except (
        RecommendationCourseIdentifierFormatError,
        RecommendationCourseIdentifierError,
        RecommendationInvalidCourseResultError,
    ) as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return SendSavedCourseEmailResponse(
            request_id="",
            status="failed",
            recipient_email=str(request.recipient_email),
            course_id=request.course_id,
            course_title=request.course_title,
            failure_reason=str(error),
        )

    if result.status == "failed":
        response.status_code = status.HTTP_502_BAD_GATEWAY
    return result
