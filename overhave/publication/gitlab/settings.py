from overhave.base_settings import BaseOverhavePrefix
from overhave.transport.http.gitlab_client import GitlabBranch, GitlabRepository


class NotSpecifiedFeatureTypeError(RuntimeError):
    """ Exception for not specified reviewers relative to feature type. """


class OverhaveGitlabPublisherSettings(BaseOverhavePrefix):
    """ Settings for :class:`GitlabVersionPublisher`.

    This is a representation of Gitlab project parameters.
    Some merge-request parameters are also could be defined through these settings.
    """

    repository_id: str  # for example '2034'
    default_target_branch_name: str = "master"

    @property
    def repository(self) -> GitlabRepository:
        return GitlabRepository(project_id=self.repository_id)

    @property
    def target_branch(self) -> GitlabBranch:
        return GitlabBranch(project_id=self.repository_id, branch=self.default_target_branch_name)
