from pydantic import BaseModel


class EventTrackingErrorResponse(BaseModel):
    code: str
    message: str
    field: str | None = None
    invalid_value: str | None = None
