from pydantic import BaseModel, Field


class CourseDetailItemResponse(BaseModel):
    sequence: int
    component_type: str
    name: str
    description: str
    keywords: list[str]


class RecommendationCourseDetailConditionResponse(BaseModel):
    place: str
    time_slot: str
    activity_type: str
    transportation: str


class RecommendationCourseDetailSummaryResponse(BaseModel):
    total_detail_items: int
    restaurant_count: int
    cafe_count: int
    activity_count: int


class RecommendationCourseDetailResponse(BaseModel):
    recommendation_id: str
    course_id: str
    course_title: str
    request_condition: RecommendationCourseDetailConditionResponse
    summary: RecommendationCourseDetailSummaryResponse
    detail_items: list[CourseDetailItemResponse] = Field(min_length=3)
