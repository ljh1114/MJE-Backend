from dataclasses import dataclass

from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)
from app.domains.recommendation.entities.course_detail_item import CourseDetailItem


@dataclass(frozen=True)
class CourseDetail:
    course_id: str
    course_title: str
    recommendation_id: str
    condition: RecommendationCondition
    detail_items: list[CourseDetailItem]
