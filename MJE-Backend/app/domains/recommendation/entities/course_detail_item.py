from dataclasses import dataclass


@dataclass(frozen=True)
class CourseDetailItem:
    sequence: int
    component_type: str
    name: str
    description: str
    keywords: list[str]
