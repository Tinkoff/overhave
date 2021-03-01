from typing import cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave.transport import S3Manager, S3ManagerSettings


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


@pytest.fixture(scope="class")
def mocked_boto3_client() -> mock.MagicMock:
    mocked_client = mock.MagicMock()
    mocked_client.list_buckets.return_value = {"Buckets": []}
    with mock.patch("boto3.client", return_value=mocked_client):
        yield


@pytest.fixture()
def test_s3_manager(test_s3_manager_settings: S3ManagerSettings, mocked_boto3_client: mock.MagicMock) -> S3Manager:
    return S3Manager(test_s3_manager_settings)
