from pydantic import BaseModel


class SavedCourseResponse(BaseModel):
    saved_course_id: str
