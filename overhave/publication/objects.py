import enum


class PublicationManagerType(enum.StrEnum):
    """Enum that declares remotely manager for publication pull requests."""

    GITLAB = "gitlab"
    STASH = "stash"
