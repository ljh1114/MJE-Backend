from typing import Literal

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    place: Literal["gangnam", "seongsu", "hongdae", "jamsil"]
    time_slot: Literal["morning", "afternoon", "evening", "night"]
    activity_type: Literal["cafe", "culture", "activity", "walk", "dining"]
    transportation: Literal["car", "public_transport"]
