from app.core.exceptions import ApplicationError


class RecommendationError(ApplicationError):
    """Recommendation domain exception."""


class RecommendationRuleNotMatchedError(RecommendationError):
    """Raised when no recommendation rule matches the request."""
