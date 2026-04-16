from pydantic import BaseModel, Field


class CourseItemResponse(BaseModel):
    course_type: str
    title: str
    place_name: str
    keywords: list[str]


class RecommendationResponse(BaseModel):
    recommendation_id: str
    main_course: CourseItemResponse
    secondary_courses: list[CourseItemResponse] = Field(min_length=2, max_length=2)
