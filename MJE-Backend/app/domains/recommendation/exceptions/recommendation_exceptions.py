from app.core.exceptions import ApplicationError


class RecommendationError(ApplicationError):
    """Recommendation domain exception."""


class RecommendationInvalidInputError(RecommendationError):
    """Raised when recommendation input is invalid."""

    def __init__(self, field_name: str, field_value: str, allowed_values: list[str]) -> None:
        self.field_name = field_name
        self.field_value = field_value
        self.allowed_values = allowed_values
        self.error_code = "RECOMMENDATION_INVALID_INPUT"
        super().__init__(
            f"Invalid value for '{field_name}': '{field_value}'. "
            f"Allowed values: {', '.join(allowed_values)}."
        )


class RecommendationRuleNotMatchedError(RecommendationError):
    """Raised when no recommendation rule matches the request."""
