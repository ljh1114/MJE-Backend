from dataclasses import dataclass

from app.domains.recommendation.entities.course_detail_item import CourseDetailItem


@dataclass(frozen=True)
class CourseDetail:
    course_id: str
    course_title: str
    detail_items: list[CourseDetailItem]
