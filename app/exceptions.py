
class TaskNotFoundError(Exception):
    """Raised when a requested task does not exist."""


class InvalidTaskError(Exception):
    """Raised when a task operation violates business rules."""
