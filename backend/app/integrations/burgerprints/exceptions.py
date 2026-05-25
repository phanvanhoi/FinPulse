class BurgerPrintsError(Exception):
    """Base error for BurgerPrints API integration."""


class BurgerPrintsAuthError(BurgerPrintsError):
    """Invalid or missing API key."""


class BurgerPrintsAPIError(BurgerPrintsError):
    """API request failed with a client or server error."""

    def __init__(self, message: str, status_code: int | None = None, errors: list | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.errors = errors or []
