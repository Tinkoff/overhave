from typing import List, Mapping, Sequence

import pytest
from faker import Faker

from overhave.entities import FeatureTypeName, OverhaveFileSettings, OverhaveStashManagerSettings
from overhave.entities.stash.manager.stash_manager import StashProjectManager
from overhave.scenario import FileManager
from overhave.transport import (
    StashBranch,
    StashHttpClient,
    StashProject,
    StashRepository,
    StashReviewer,
    StashReviewerInfo,
)
from tests.objects import get_file_settings


@pytest.mark.parametrize("test_file_settings", [get_file_settings()], indirect=True)
class TestStashProjectManager:
    """ Unit tests for :class:`StashProjectManager`. """

    def test_stash_project_settings_basic(
        self,
        test_stash_project_settings_with_default_reviewers: OverhaveStashManagerSettings,
        test_file_settings: OverhaveFileSettings,
        mocked_stash_client: StashHttpClient,
        mocked_file_manager: FileManager,
        test_repository_name: str,
        test_project_key: str,
        test_target_branch: str,
    ):
        manager = StashProjectManager(
            stash_project_settings=test_stash_project_settings_with_default_reviewers,
            file_settings=test_file_settings,
            client=mocked_stash_client,
            file_manager=mocked_file_manager,
            task_links_keyword=None,
        )
        correct_repository = StashRepository(slug=test_repository_name, project=StashProject(key=test_project_key))
        assert manager._stash_project_settings.repository == correct_repository
        assert manager._stash_project_settings.target_branch == StashBranch(
            id=test_target_branch, repository=correct_repository
        )

    def test_stash_project_settings_with_default_reviewers(
        self,
        test_stash_project_settings_with_default_reviewers: OverhaveStashManagerSettings,
        test_file_settings: OverhaveFileSettings,
        mocked_stash_client: StashHttpClient,
        mocked_file_manager: FileManager,
        test_default_reviewers: Sequence[str],
        faker: Faker,
    ):
        manager = StashProjectManager(
            stash_project_settings=test_stash_project_settings_with_default_reviewers,
            file_settings=test_file_settings,
            client=mocked_stash_client,
            file_manager=mocked_file_manager,
            task_links_keyword=None,
        )
        assert manager._stash_project_settings.get_reviewers(faker.word()) == [
            StashReviewer(user=StashReviewerInfo(name=reviewer)) for reviewer in test_default_reviewers
        ]

    def test_stash_project_settings_with_reviewers_mapping(
        self,
        test_stash_project_settings_with_reviewers_mapping: OverhaveStashManagerSettings,
        test_file_settings: OverhaveFileSettings,
        mocked_stash_client: StashHttpClient,
        mocked_file_manager: FileManager,
        test_reviewers_mapping: Mapping[FeatureTypeName, List[str]],
        faker: Faker,
    ):
        manager = StashProjectManager(
            stash_project_settings=test_stash_project_settings_with_reviewers_mapping,
            file_settings=test_file_settings,
            client=mocked_stash_client,
            file_manager=mocked_file_manager,
            task_links_keyword=None,
        )
        for key in test_reviewers_mapping.keys():
            assert manager._stash_project_settings.get_reviewers(key) == [
                StashReviewer(user=StashReviewerInfo(name=reviewer)) for reviewer in test_reviewers_mapping[key]
            ]
