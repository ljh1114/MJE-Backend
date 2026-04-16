from pydantic import BaseModel


class SavedCourseErrorResponse(BaseModel):
    code: str
    message: str
    field: str | None = None
    invalid_value: str | None = None
