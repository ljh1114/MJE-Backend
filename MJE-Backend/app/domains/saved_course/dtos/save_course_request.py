from pydantic import BaseModel


class SaveCourseRequest(BaseModel):
    recommendation_id: str
