from pydantic import BaseModel, EmailStr, Field


class SendSavedCourseEmailRequest(BaseModel):
    recipient_email: EmailStr
    course_id: str = Field(pattern=r"^course-[a-z]+-main$")
    course_title: str = Field(min_length=1, max_length=100)
