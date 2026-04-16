from pydantic import BaseModel


class EventResponse(BaseModel):
    event_id: str
    status: str
