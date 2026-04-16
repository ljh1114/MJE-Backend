from dataclasses import dataclass

from app.domains.recommendation.entities.course import Course
from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)


@dataclass(frozen=True)
class RecommendationRule:
    rule_name: str
    condition: RecommendationCondition
    main_course_template: Course
    secondary_course_templates: list[Course]
