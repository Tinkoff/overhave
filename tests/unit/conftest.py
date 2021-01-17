import pytest

from overhave.entities import OverhaveScenarioCompilerSettings


@pytest.fixture(scope="session")
def test_compilation_settings() -> OverhaveScenarioCompilerSettings:
    return OverhaveScenarioCompilerSettings()
