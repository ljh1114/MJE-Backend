from app.domains.saved_course.dtos.send_saved_course_email_request import (
    SendSavedCourseEmailRequest,
)
from app.domains.saved_course.services.saved_course_service import SavedCourseService


def test_create_email_send_request_returns_requested_status() -> None:
    service = SavedCourseService()

    result = service.create_email_send_request(
        SendSavedCourseEmailRequest(
            recipient_email="user@example.com",
            course_id="course-gangnam-main",
            course_title="강남 감성 다이닝 데이트",
        )
    )

    assert result.status == "requested"
    assert result.recipient_email == "user@example.com"
    assert result.course_id == "course-gangnam-main"
    assert result.course_title == "강남 감성 다이닝 데이트"
