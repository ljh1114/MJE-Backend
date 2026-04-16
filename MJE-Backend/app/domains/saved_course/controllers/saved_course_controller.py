from fastapi import APIRouter, status

from app.domains.saved_course.dtos.send_saved_course_email_request import (
    SendSavedCourseEmailRequest,
)
from app.domains.saved_course.dtos.send_saved_course_email_response import (
    SendSavedCourseEmailResponse,
)
from app.domains.saved_course.dtos.saved_course_error_response import (
    SavedCourseErrorResponse,
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
) -> SendSavedCourseEmailResponse:
    return saved_course_service.create_email_send_request(request)
