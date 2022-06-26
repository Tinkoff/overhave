from typing import List, Mapping, Sequence

import pytest
from faker import Faker

from overhave.publication.gitlab import GitlabVersionPublisher
from overhave.storage import FeatureTypeName
from overhave.transport import GitlabRepository
from tests.objects import get_test_file_settings


@pytest.mark.parametrize("test_task_tracker_url", [None], indirect=True)
@pytest.mark.parametrize("test_file_settings", [get_test_file_settings()], indirect=True)
class TestGitlabProjectManager:
    """Unit tests for :class:`GitlabVersionPublisher`."""

    def test_gitlab_project_settings_basic(
        self,
        test_target_branch: str,
        test_repository_id_or_name: str,
        test_project_key: str,
        test_gitlab_publisher_with_default_reviewers: GitlabVersionPublisher,
    ) -> None:
        correct_repository = GitlabRepository(project_id=test_repository_id_or_name)
        assert test_gitlab_publisher_with_default_reviewers._gitlab_publisher_settings.repository == correct_repository
        assert (
            test_gitlab_publisher_with_default_reviewers._gitlab_publisher_settings.target_branch == test_target_branch
        )

    def test_gitlab_project_settings_with_default_reviewers(
        self,
        test_default_reviewers: Sequence[str],
        test_gitlab_publisher_with_default_reviewers: GitlabVersionPublisher,
        faker: Faker,
    ) -> None:
        assert (
            test_gitlab_publisher_with_default_reviewers._gitlab_publisher_settings.get_reviewers(faker.word())
            == test_default_reviewers
        )

    def test_gitlab_project_settings_with_reviewers_mapping(
        self,
        test_reviewers_mapping: Mapping[FeatureTypeName, List[str]],
        test_gitlab_publisher_with_reviewers_mapping: GitlabVersionPublisher,
        faker: Faker,
    ) -> None:
        for key in test_reviewers_mapping.keys():
            assert test_gitlab_publisher_with_reviewers_mapping._gitlab_publisher_settings.get_reviewers(key) == list(
                test_reviewers_mapping[key]
            )
