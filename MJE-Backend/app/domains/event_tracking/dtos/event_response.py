from pydantic import BaseModel


class EventResponse(BaseModel):
    accepted: bool = True
