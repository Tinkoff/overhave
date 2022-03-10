import pytest
from fastapi.testclient import TestClient

from overhave import overhave_api
from overhave.entities import TestUserSpecification


@pytest.fixture()
def test_api_client(database: None) -> TestClient:
    return TestClient(overhave_api())


@pytest.fixture(scope="module")
def test_new_specification() -> TestUserSpecification:
    return TestUserSpecification({"new_test": "new_value"})
