import abc
import logging
from typing import Optional

import git

from overhave.entities import PublisherContext
from overhave.publication.base_publisher import BaseVersionPublisher, BaseVersionPublisherException

logger = logging.getLogger(__name__)


class BaseGitVersionPublisherError(BaseVersionPublisherException):
    """ Base exception for git version publisher. """


class CurrentBranchEqualToDefaultError(BaseGitVersionPublisherError):
    """ Exception for situation when current branch is equal to default branch. """


class CurrentBranchNotEqualToTargetError(BaseGitVersionPublisherError):
    """ Exception for situation when current branch is not equal to target branch. """


class CommitNotCreatedError(BaseGitVersionPublisherError):
    """ Exception for situation with not created commit. """


class NullablePullRequestUrlError(BaseGitVersionPublisherError):
    """ Exception for nullable merge-request in selected Draft. """


class GitVersionPublisher(BaseVersionPublisher, abc.ABC):
    """ Class for feature version's management, based on git. """

    @staticmethod
    def _create_head(name: str, repository: git.Repo) -> git.Head:
        origin: git.Head = repository.remotes.origin
        origin.pull()
        logger.info("Origin successfully pulled")
        if name in repository.heads:
            repository.delete_head(repository.heads[name], force=True)
            logger.warning("Trashed existed branch with name '%s'", name)

        branch = repository.create_head(name)
        logger.info("Created head for branch: %s", branch)
        assert (
            repository.active_branch != branch
        ), f"Active branch '{repository.active_branch.name}' is not '{branch.name}'!"
        return branch

    def _create_commit_and_push(self, context: PublisherContext, repository: git.Repo, target_branch: git.Head) -> None:
        original_branch = repository.active_branch
        changes_pushed = False
        try:
            target_branch.checkout()
            logger.info("Active branch after checkout: %s", repository.active_branch)

            feature_file = self._file_manager.produce_feature_file(context=context)
            logger.info("Untracked files after feature creation: %s", repository.untracked_files)
            repository.index.add([feature_file.as_posix()])
            logger.info("Untracked files after index update: %s", repository.untracked_files)

            repository.index.commit(
                (
                    f"Added feature {context.feature.name} "
                    f"(id {context.feature.id}) "
                    f"by {context.test_run.executed_by}"
                ),
                skip_hooks=True,
            )
            logger.info("Commit successfully created")
            if repository.active_branch == original_branch:
                raise CurrentBranchEqualToDefaultError(
                    f"Current branch could not be equal to default: '{original_branch}'!"
                )
            if repository.active_branch != target_branch:
                raise CurrentBranchNotEqualToTargetError(
                    f"Current branch should be equal to target: '{target_branch}'!"
                )

            logger.info("Remote origin url: %s", repository.remotes.origin.url)
            repository.git.push("origin", target_branch, force=True)
            logger.info("Changes successfully pushed to remote repository")
            changes_pushed = True
        except (git.GitCommandError, BaseGitVersionPublisherError):
            logger.exception("Error while trying to commit feature file!")

        if original_branch != repository.active_branch:
            logger.info("Current branch is '%s'", repository.active_branch)
            original_branch.checkout()
            logger.info("Branch returned to '%s'", repository.active_branch)

        if not changes_pushed:
            raise CommitNotCreatedError("Commit has not been created!")

    def _push_version(self, draft_id: int) -> Optional[PublisherContext]:
        try:
            logger.debug("Initialize git repository in '%s'...", self._file_settings.work_dir)
            repository = git.Repo(self._file_settings.work_dir)
            logger.info("Repository: %s", repository)
            logger.info("Working dir: %s", repository.working_dir)
            logger.info("Active head: %s", repository.active_branch)

            ctx = self._compile_context(draft_id)
            git_branch = self._create_head(repository=repository, name=ctx.target_branch)
            self._create_commit_and_push(context=ctx, repository=repository, target_branch=git_branch)
            return ctx
        except git.InvalidGitRepositoryError:
            logger.exception("Error while trying to initialize git repository!")
        except (git.GitCommandError, BaseGitVersionPublisherError):
            logger.exception("Error while trying to push scenario version!")
        return None

    def _save_as_duplicate(self, context: PublisherContext) -> None:
        previous_draft = self._draft_storage.get_previous_feature_draft(context.feature.id)
        if previous_draft.pr_url is None:
            raise NullablePullRequestUrlError(
                "Previous draft with id=%s has not got pull-request URL!", previous_draft.id
            )
        if previous_draft.published_at is None:
            raise RuntimeError
        self._draft_storage.save_response(
            draft_id=context.draft.id,
            pr_url=previous_draft.pr_url,
            published_at=previous_draft.published_at,
            opened=True,
        )
