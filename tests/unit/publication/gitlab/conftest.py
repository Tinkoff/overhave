from typing import List, Mapping, Sequence, cast

import pytest
from pytest_mock import MockFixture

from overhave import OverhaveFileSettings, OverhaveProjectSettings
from overhave.entities import FeatureTypeName
from overhave.publication.gitlab import GitlabVersionPublisher, OverhaveGitlabPublisherSettings
from overhave.scenario import FileManager
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
from overhave.transport import GitlabHttpClient


@pytest.fixture()
def test_gitlab_publisher_settings_with_default_reviewers(
    test_repository_id_or_name: str, test_target_branch: str, test_default_reviewers: Sequence[str],
) -> OverhaveGitlabPublisherSettings:
    return OverhaveGitlabPublisherSettings(
        repository_id=test_repository_id_or_name,
        default_target_branch_name=test_target_branch,
        default_reviewers=test_default_reviewers,
    )


@pytest.fixture()
def test_gitlab_project_settings_with_reviewers_mapping(
    test_repository_id_or_name: str,
    test_target_branch: str,
    test_reviewers_mapping: Mapping[FeatureTypeName, List[str]],
) -> OverhaveGitlabPublisherSettings:
    return OverhaveGitlabPublisherSettings(
        repository_id=test_repository_id_or_name,
        default_target_branch_name=test_target_branch,
        feature_type_to_reviewers_mapping=test_reviewers_mapping,
    )


@pytest.fixture()
def mocked_gitlab_client(mocker: MockFixture) -> GitlabHttpClient:
    return cast(GitlabHttpClient, mocker.create_autospec(GitlabHttpClient))


@pytest.fixture()
def test_gitlab_publisher_with_default_reviewers(
    test_file_settings: OverhaveFileSettings,
    test_project_settings: OverhaveProjectSettings,
    test_gitlab_publisher_settings_with_default_reviewers: OverhaveGitlabPublisherSettings,
    mocked_file_manager: FileManager,
    mocked_gitlab_client: GitlabHttpClient,
    mocker: MockFixture,
) -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        file_settings=test_file_settings,
        project_settings=test_project_settings,
        feature_storage=mocker.create_autospec(IFeatureStorage),
        scenario_storage=mocker.create_autospec(IScenarioStorage),
        test_run_storage=mocker.create_autospec(ITestRunStorage),
        draft_storage=mocker.create_autospec(IDraftStorage),
        file_manager=mocked_file_manager,
        gitlab_publisher_settings=test_gitlab_publisher_settings_with_default_reviewers,
        client=mocked_gitlab_client,
    )


@pytest.fixture()
def test_gitlab_publisher_with_reviewers_mapping(
    test_file_settings: OverhaveFileSettings,
    test_project_settings: OverhaveProjectSettings,
    test_gitlab_project_settings_with_reviewers_mapping: OverhaveGitlabPublisherSettings,
    mocked_file_manager: FileManager,
    mocked_gitlab_client: GitlabHttpClient,
    mocker: MockFixture,
) -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        file_settings=test_file_settings,
        project_settings=test_project_settings,
        feature_storage=mocker.create_autospec(IFeatureStorage),
        scenario_storage=mocker.create_autospec(IScenarioStorage),
        test_run_storage=mocker.create_autospec(ITestRunStorage),
        draft_storage=mocker.create_autospec(IDraftStorage),
        file_manager=mocked_file_manager,
        gitlab_publisher_settings=test_gitlab_project_settings_with_reviewers_mapping,
        client=mocked_gitlab_client,
    )
