from dataclasses import dataclass

from app.domains.recommendation.entities.course import Course
from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)


@dataclass(frozen=True)
class Recommendation:
    recommendation_id: str
    condition: RecommendationCondition
    main_course: Course
    secondary_courses: list[Course]
