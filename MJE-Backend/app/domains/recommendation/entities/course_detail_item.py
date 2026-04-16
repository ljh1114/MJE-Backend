from dataclasses import dataclass


@dataclass(frozen=True)
class CourseDetailItem:
    component_type: str
    name: str
    description: str
    keywords: list[str]
