from app.core.exceptions import ApplicationError


class EventTrackingError(ApplicationError):
    """Event tracking domain exception."""


class EventTrackingInvalidInputError(EventTrackingError):
    """Raised when event tracking input violates domain rules."""

    def __init__(
        self,
        *,
        field_name: str,
        field_value: str,
        message: str,
    ) -> None:
        self.field_name = field_name
        self.field_value = field_value
        self.error_code = "EVENT_TRACKING_INVALID_INPUT"
        super().__init__(message)
