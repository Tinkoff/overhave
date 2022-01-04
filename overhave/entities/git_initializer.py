import logging

import git

from overhave.entities.settings import OverhaveFileSettings

logger = logging.getLogger(__name__)


class BaseGitRepositoryInitializerException(Exception):
    """Base exception for GitRepositoryInitializer."""


class GitRepositoryInitializationError(BaseGitRepositoryInitializerException):
    """Error for situation with `git.GitError` when repo initializing."""


class GitPullError(BaseGitRepositoryInitializerException):
    """Error for situation with `git.GitError` when origin pulling."""


class GitRepositoryInitializer:
    """Class for git repository initializing and updating with pull command."""

    def __init__(self, file_settings: OverhaveFileSettings) -> None:
        self._file_settings = file_settings

        self._init_repository()

    def _init_repository(self) -> None:
        try:
            logger.debug("Initialize git repository in '%s'...", self._file_settings.features_dir)
            self._repository = git.Repo(self._file_settings.features_dir)
            logger.info("Repository: %s", self._repository)
            logger.info("Working dir: %s", self._repository.working_dir)
            logger.info("Active head: %s", self._repository.active_branch)
        except git.GitError as err:
            raise GitRepositoryInitializationError("Error while trying to initialize git repository!") from err

    @property
    def repository(self) -> git.Repo:
        return self._repository

    def pull(self) -> None:
        try:
            origin = self._repository.remotes.origin
            origin.pull()
            logger.info("Origin successfully pulled")
        except git.GitError as err:
            raise GitPullError("Error while trying to pull from remote repository!") from err
