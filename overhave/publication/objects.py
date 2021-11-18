import enum


class PublicationManagerType(str, enum.Enum):
    """Enum that declares remotely manager for publication pull requests."""

    GITLAB = "gitlab"
    STASH = "stash"
