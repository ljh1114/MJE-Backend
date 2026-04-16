from pydantic import BaseModel, Field


class CourseItemResponse(BaseModel):
    course_type: str
    title: str
    place_name: str
    keywords: list[str]


class RecommendationConditionResponse(BaseModel):
    place: str
    time_slot: str
    activity_type: str
    transportation: str


class RecommendationSummaryResponse(BaseModel):
    total_courses: int
    main_course_count: int
    secondary_course_count: int


class RecommendationResponse(BaseModel):
    recommendation_id: str
    request_condition: RecommendationConditionResponse
    summary: RecommendationSummaryResponse
    main_course: CourseItemResponse
    secondary_courses: list[CourseItemResponse] = Field(min_length=2, max_length=2)
    courses: list[CourseItemResponse] = Field(min_length=3, max_length=3)
