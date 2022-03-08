import pytest
from fastapi.testclient import TestClient

from overhave import overhave_api


@pytest.fixture()
def test_api_client(database: None) -> TestClient:
    return TestClient(overhave_api())
