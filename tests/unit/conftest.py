from typing import Callable, cast

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockFixture

from overhave import (
    OverhaveFileSettings,
    OverhaveProjectSettings,
    OverhaveScenarioCompilerSettings,
    OverhaveScenarioParserSettings,
)
from overhave.entities import FeatureExtractor, GitRepositoryInitializer
from overhave.factory import IAdminFactory
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.scenario import FileManager


@pytest.fixture(scope="session")
def test_compilation_settings() -> OverhaveScenarioCompilerSettings:
    return OverhaveScenarioCompilerSettings()


@pytest.fixture(scope="session")
def test_parser_settings() -> OverhaveScenarioParserSettings:
    return OverhaveScenarioParserSettings()


@pytest.fixture()
def test_file_settings(request: FixtureRequest) -> OverhaveFileSettings:
    if hasattr(request, "param"):
        return cast(OverhaveFileSettings, request.param)
    raise NotImplementedError


@pytest.fixture()
def mocked_file_manager(mocker: MockFixture) -> FileManager:
    return cast(FileManager, mocker.create_autospec(FileManager))


@pytest.fixture()
def mocked_git_initializer(mocker: MockFixture) -> GitRepositoryInitializer:
    return cast(GitRepositoryInitializer, mocker.create_autospec(GitRepositoryInitializer))


@pytest.fixture()
def task_tracker_url(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str | None, request.param)
    return None


@pytest.fixture()
def tasks_keyword(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str, request.param)
    return None


@pytest.fixture()
def git_project_url(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str | None, request.param)
    return None


@pytest.fixture()
def test_project_settings(
    task_tracker_url: str | None, tasks_keyword: str | None, git_project_url: str | None
) -> OverhaveProjectSettings:
    return OverhaveProjectSettings(
        task_tracker_url=task_tracker_url, tasks_keyword=tasks_keyword, git_project_url=git_project_url
    )


@pytest.fixture()
def test_feature_extractor(request: FixtureRequest) -> FeatureExtractor:
    if hasattr(request, "param"):
        return cast(FeatureExtractor, request.param)
    raise NotImplementedError


@pytest.fixture()
def patched_admin_factory(
    mocked_context: BaseFactoryContext, clean_admin_factory: Callable[[], IAdminFactory]
) -> IAdminFactory:
    factory = clean_admin_factory()
    factory.set_context(mocked_context)
    return factory
