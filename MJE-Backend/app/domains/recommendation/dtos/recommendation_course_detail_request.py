from pydantic import BaseModel, field_validator


class RecommendationCourseDetailRequest(BaseModel):
    course_id: str

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, value: str) -> str:
        normalized_value = value.strip().lower()
        if not normalized_value:
            raise ValueError("course_id must not be blank.")
        return normalized_value
