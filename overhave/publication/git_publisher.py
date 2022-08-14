import abc
import logging
from typing import Generic, Optional, cast

import git

from overhave.entities import GitPullError, GitRepositoryInitializer, OverhaveFileSettings
from overhave.publication.base_publisher import BaseVersionPublisher, BaseVersionPublisherException
from overhave.publication.settings import GitPublisherSettings
from overhave.scenario import FileManager, OverhaveProjectSettings
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage, PublisherContext

logger = logging.getLogger(__name__)


class BaseGitVersionPublisherError(BaseVersionPublisherException):
    """Base exception for git version publisher."""


class CurrentBranchEqualToDefaultError(BaseGitVersionPublisherError):
    """Exception for situation when current branch is equal to default branch."""


class CurrentBranchNotEqualToTargetError(BaseGitVersionPublisherError):
    """Exception for situation when current branch is not equal to target branch."""


class CommitNotCreatedError(BaseGitVersionPublisherError):
    """Exception for situation with not created commit."""


class GitVersionPublisher(Generic[GitPublisherSettings], BaseVersionPublisher, abc.ABC):
    """Class for feature version's management, based on git."""

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        project_settings: OverhaveProjectSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        test_run_storage: ITestRunStorage,
        draft_storage: IDraftStorage,
        file_manager: FileManager,
        git_initializer: GitRepositoryInitializer,
    ) -> None:
        super().__init__(
            file_settings=file_settings,
            project_settings=project_settings,
            feature_storage=feature_storage,
            scenario_storage=scenario_storage,
            test_run_storage=test_run_storage,
            draft_storage=draft_storage,
            file_manager=file_manager,
        )
        self._git_initializer = git_initializer

    def _create_head(self, name: str) -> git.SymbolicReference:
        repo = self._git_initializer.repository
        if name in repo.heads:
            repo.delete_head(repo.heads[name], force=True)
            logger.warning("Trashed existed branch with name '%s'", name)

        branch = repo.create_head(name)
        logger.info("Created head for branch: %s", branch)
        assert repo.active_branch != branch, f"Active branch '{repo.active_branch.name}' is not '{branch.name}'!"
        return branch

    def _create_commit_and_push(self, context: PublisherContext, target_branch: git.Head) -> None:
        repo = self._git_initializer.repository
        original_branch = repo.active_branch
        changes_pushed = False
        try:
            target_branch.checkout()
            logger.info("Active branch after checkout: %s", repo.active_branch)

            feature_file = self._file_manager.produce_feature_file(context=context)
            logger.info("Untracked files after feature creation: %s", repo.untracked_files)
            repo.index.add([feature_file.as_posix()])
            logger.info("Untracked files after index update: %s", repo.untracked_files)

            repo.index.commit(
                (
                    f"Added feature {context.feature.name} "
                    f"(id {context.feature.id}) "
                    f"by {context.test_run.executed_by}"
                ),
                skip_hooks=True,
            )
            logger.info("Commit successfully created")
            if repo.active_branch == original_branch:
                raise CurrentBranchEqualToDefaultError(
                    f"Current branch could not be equal to default: '{original_branch}'!"
                )
            if repo.active_branch != target_branch:
                raise CurrentBranchNotEqualToTargetError(
                    f"Current branch should be equal to target: '{target_branch}'!"
                )

            logger.info("Remote origin url: %s", repo.remotes.origin.url)
            repo.git.push("origin", target_branch, force=True)
            logger.info("Changes successfully pushed to remote repository")
            changes_pushed = True
        except (git.GitCommandError, BaseGitVersionPublisherError):
            logger.exception("Error while trying to commit feature file!")

        if original_branch != repo.active_branch:
            logger.info("Current branch is '%s'", repo.active_branch)
            original_branch.checkout()
            logger.info("Branch returned to '%s'", repo.active_branch)

        if not changes_pushed:
            raise CommitNotCreatedError("Commit has not been created!")

    def _push_version(self, draft_id: int) -> Optional[PublisherContext]:
        try:
            self._git_initializer.pull()
            ctx = self._compile_context(draft_id)
            git_branch = cast(git.Head, self._create_head(name=ctx.target_branch))
            self._create_commit_and_push(context=ctx, target_branch=git_branch)
            return ctx
        except GitPullError:
            logger.exception("Error while trying to pull remote repository!")
        except (git.GitCommandError, BaseGitVersionPublisherError):
            logger.exception("Error while trying to push scenario version!")
        return None
