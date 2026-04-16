from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationCondition:
    place: str
    time_slot: str
    activity_type: str
    transportation: str
