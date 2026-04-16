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


class RecommendationCourseIdentifierError(RecommendationError):
    """Raised when course identifier is invalid."""

    def __init__(self, course_id: str) -> None:
        self.course_id = course_id
        self.error_code = "RECOMMENDATION_COURSE_IDENTIFIER_INVALID"
        super().__init__(f"Invalid recommendation course identifier: '{course_id}'.")


class RecommendationCourseIdentifierFormatError(RecommendationError):
    """Raised when course identifier format is invalid."""

    def __init__(self, course_id: str) -> None:
        self.course_id = course_id
        self.error_code = "RECOMMENDATION_COURSE_IDENTIFIER_INVALID_FORMAT"
        super().__init__(
            "Recommendation course identifier must match the format "
            "'course-<place>-main'."
        )


class RecommendationInvalidCourseResultError(RecommendationError):
    """Raised when stored course result is incomplete or invalid."""

    def __init__(self, course_id: str, reason: str) -> None:
        self.course_id = course_id
        self.reason = reason
        self.error_code = "RECOMMENDATION_INVALID_COURSE_RESULT"
        super().__init__(
            f"Recommendation course result is invalid for '{course_id}': {reason}."
        )
