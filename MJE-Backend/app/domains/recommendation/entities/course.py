from dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    course_type: str
    title: str
    place_name: str
    keywords: list[str]
