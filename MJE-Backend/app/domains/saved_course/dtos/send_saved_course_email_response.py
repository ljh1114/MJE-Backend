from pydantic import BaseModel


class SendSavedCourseEmailResponse(BaseModel):
    request_id: str
    status: str
    recipient_email: str
    course_id: str
    course_title: str
