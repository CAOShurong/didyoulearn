"""Project-specific exceptions."""


class DidYouLearnError(Exception):
    """Base exception for expected user-facing failures."""


class ValidationFailure(DidYouLearnError):
    """Raised when a task or run does not satisfy the public schema."""


class StudyDesignError(DidYouLearnError):
    """Raised when an allocation or analysis would violate protocol constraints."""
