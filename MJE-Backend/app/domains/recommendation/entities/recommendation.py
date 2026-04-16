from dataclasses import dataclass

from app.domains.recommendation.entities.course import Course


@dataclass(frozen=True)
class Recommendation:
    recommendation_id: str
    main_course: Course
    secondary_courses: list[Course]
