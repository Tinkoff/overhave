class BaseGitVersionPublisherError(Exception):
    """Base exception for git version publisher."""


class CurrentBranchEqualToDefaultError(BaseGitVersionPublisherError):
    """Exception for situation when current branch is equal to default branch."""


class CurrentBranchNotEqualToTargetError(BaseGitVersionPublisherError):
    """Exception for situation when current branch is not equal to target branch."""


class CommitNotCreatedError(BaseGitVersionPublisherError):
    """Exception for situation with not created commit."""
