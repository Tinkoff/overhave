from typing import List, Mapping, Sequence

import pytest
from faker import Faker

from overhave.entities import FeatureTypeName
from overhave.publication import StashVersionPublisher
from overhave.transport import StashBranch, StashProject, StashRepository, StashReviewer, StashReviewerInfo
from tests.objects import get_test_file_settings


@pytest.mark.parametrize("test_browse_url", [None], indirect=True)
@pytest.mark.parametrize("test_file_settings", [get_test_file_settings()], indirect=True)
class TestStashProjectManager:
    """Unit tests for :class:`StashVersionPublisher`."""

    def test_stash_project_settings_basic(
        self,
        test_target_branch: str,
        test_repository_id_or_name: str,
        test_project_key: str,
        test_stash_publisher_with_default_reviewers: StashVersionPublisher,
    ) -> None:
        correct_repository = StashRepository(
            slug=test_repository_id_or_name, project=StashProject(key=test_project_key)
        )
        assert test_stash_publisher_with_default_reviewers._stash_publisher_settings.repository == correct_repository
        assert test_stash_publisher_with_default_reviewers._stash_publisher_settings.target_branch == StashBranch(
            id=test_target_branch, repository=correct_repository
        )

    def test_stash_project_settings_with_default_reviewers(
        self,
        test_default_reviewers: Sequence[str],
        test_stash_publisher_with_default_reviewers: StashVersionPublisher,
        faker: Faker,
    ) -> None:
        assert test_stash_publisher_with_default_reviewers._stash_publisher_settings.get_reviewers(faker.word()) == [
            StashReviewer(user=StashReviewerInfo(name=reviewer)) for reviewer in test_default_reviewers
        ]

    def test_stash_project_settings_with_reviewers_mapping(
        self,
        test_reviewers_mapping: Mapping[FeatureTypeName, List[str]],
        test_stash_publisher_with_reviewers_mapping: StashVersionPublisher,
        faker: Faker,
    ) -> None:
        for key in test_reviewers_mapping.keys():
            assert test_stash_publisher_with_reviewers_mapping._stash_publisher_settings.get_reviewers(key) == [
                StashReviewer(user=StashReviewerInfo(name=reviewer)) for reviewer in test_reviewers_mapping[key]
            ]
