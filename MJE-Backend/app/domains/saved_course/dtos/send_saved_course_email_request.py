from pydantic import BaseModel


class SendSavedCourseEmailRequest(BaseModel):
    recipient_email: str
    course_title: str
