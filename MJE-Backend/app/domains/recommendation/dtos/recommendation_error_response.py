from pydantic import BaseModel


class RecommendationErrorResponse(BaseModel):
    code: str
    message: str
    field: str | None = None
    invalid_value: str | None = None
    allowed_values: list[str] | None = None
