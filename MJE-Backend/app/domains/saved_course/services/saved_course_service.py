from uuid import uuid4

from app.domains.saved_course.dtos.send_saved_course_email_request import (
    SendSavedCourseEmailRequest,
)
from app.domains.saved_course.dtos.send_saved_course_email_response import (
    SendSavedCourseEmailResponse,
)


class SavedCourseService:
    """Use-case orchestration for saved course domain."""

    def create_email_send_request(
        self, request: SendSavedCourseEmailRequest
    ) -> SendSavedCourseEmailResponse:
        return SendSavedCourseEmailResponse(
            request_id=str(uuid4()),
            status="requested",
            recipient_email=str(request.recipient_email),
            course_id=request.course_id,
            course_title=request.course_title,
        )
