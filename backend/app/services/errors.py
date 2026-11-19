"""Domain errors raised by services. The API layer maps each kind to an HTTP status (app/api/errors.py)."""


class DomainError(Exception):
    """Base class. `code` is the stable machine-readable code; `extra` adds fields to the error body."""

    def __init__(self, code: str, **extra: object) -> None:
        super().__init__(code)
        self.code = code
        self.extra = extra


class InvalidInput(DomainError):
    """A value breaks a rule on its shape or range (HTTP 422)."""


class Forbidden(DomainError):
    """The actor's role does not allow this action (HTTP 403)."""


class NotFound(DomainError):
    """The target does not exist, or must look so to this actor (HTTP 404)."""


class Conflict(DomainError):
    """A business rule refuses the action in the current state (HTTP 409)."""
