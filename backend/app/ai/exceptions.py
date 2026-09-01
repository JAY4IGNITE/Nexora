class AIError(Exception):
    """Base class for all AI foundation exceptions."""
    pass

class AIConfigError(AIError):
    """Raised when the AI configuration is missing or invalid."""
    pass

class AIClientError(AIError):
    """Raised when the underlying AI client encounters an error (e.g., API failure)."""
    pass

class AIRetryExhaustedError(AIError):
    """Raised when all retry attempts have been exhausted."""
    pass

class AIParseError(AIError):
    """Raised when the AI output cannot be parsed into the expected structured format."""
    pass
