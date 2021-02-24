from typing import Dict, Iterator, Optional, cast

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockFixture

from overhave import OverhaveFileSettings
from overhave.entities import OverhaveScenarioCompilerSettings
from overhave.scenario import FileManager


@pytest.fixture(scope="package")
def mock_urls(envs_for_mock: Dict[str, Optional[str]], mock_default_value: str) -> Iterator[None]:
    import os

    old_values = {key: os.environ.get(key) for key in envs_for_mock}
    try:
        for key in envs_for_mock:
            os.environ[key] = envs_for_mock.get("envs_for_mock") or mock_default_value
        yield
    finally:
        for key, value in old_values.items():
            os.environ[key] = value or ""


@pytest.fixture(scope="session")
def test_compilation_settings() -> OverhaveScenarioCompilerSettings:
    return OverhaveScenarioCompilerSettings()


@pytest.fixture()
def test_file_settings(request: FixtureRequest) -> OverhaveFileSettings:
    if hasattr(request, "param"):
        return cast(OverhaveFileSettings, request.param)
    raise NotImplementedError


@pytest.fixture()
def mocked_file_manager(mocker: MockFixture) -> FileManager:
    return cast(FileManager, mocker.create_autospec(FileManager))
