import pytest

from overhave.entities import OverhaveScenarioCompilerSettings
from overhave.pytest import OverhaveProjectSettings


@pytest.fixture(scope="session")
def test_compilation_settings() -> OverhaveScenarioCompilerSettings:
    return OverhaveScenarioCompilerSettings()
