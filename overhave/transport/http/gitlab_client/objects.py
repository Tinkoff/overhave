import enum


class TokenType(enum.Enum):
    """Enum for token types you want."""

    OAUTH = "oauth"
    PRIVATE = "private"
    JOB = "job"
