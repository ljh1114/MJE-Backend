from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    place: str
    time_slot: str
    activity_type: str
    transportation: str
