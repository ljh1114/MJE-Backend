from pydantic import BaseModel, Field


class CourseDetailItemResponse(BaseModel):
    component_type: str
    name: str
    description: str
    keywords: list[str]


class RecommendationCourseDetailResponse(BaseModel):
    course_id: str
    course_title: str
    detail_items: list[CourseDetailItemResponse] = Field(min_length=3)
