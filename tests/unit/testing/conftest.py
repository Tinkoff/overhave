from typing import Optional, cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from faker import Faker
from pytest_bdd.parser import Feature, Scenario

from overhave import OverhaveProjectSettings
from tests.objects import get_file_settings


@pytest.fixture(scope="session")
def test_clean_item() -> Item:
    return cast(Item, mock.MagicMock())


@pytest.fixture()
def test_scenario_name(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_pytest_bdd_scenario(test_scenario_name: str) -> Scenario:
    scenario = mock.create_autospec(Scenario)
    setattr(scenario, "feature", mock.create_autospec(Feature))
    setattr(
        scenario.feature,
        "filename",
        get_file_settings().features_base_dir / "feature_type_1" / "full_feature_example_en.feature",
    )
    setattr(scenario, "name", test_scenario_name)
    return scenario


@pytest.fixture()
def test_pytest_bdd_item(test_pytest_bdd_scenario: Scenario) -> Item:
    item = mock.create_autospec(Item)
    setattr(item, "_obj", mock.MagicMock())
    item._obj.__scenario__ = test_pytest_bdd_scenario
    setattr(item, "own_markers", [])
    return item


@pytest.fixture()
def test_browse_url(request: FixtureRequest) -> Optional[str]:
    if hasattr(request, "param"):
        return cast(Optional[str], request.param)
    raise NotImplementedError


@pytest.fixture()
def test_project_settings(test_browse_url: Optional[str]) -> OverhaveProjectSettings:
    return OverhaveProjectSettings(browse_url=test_browse_url)