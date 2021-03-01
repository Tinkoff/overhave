from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave.transport import S3ManagerSettings


@pytest.fixture()
def test_s3_enabled(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return cast(bool, request.param)
    raise NotImplementedError


@pytest.fixture()
def test_s3_manager_settings(test_s3_enabled: bool, faker: Faker) -> S3ManagerSettings:
    return S3ManagerSettings(
        enabled=test_s3_enabled, url="https://overhave.readthedocs.io", access_key=faker.word(), secret_key=faker.word()
    )
