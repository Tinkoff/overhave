from datetime import datetime
from typing import Optional, cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave.transport import S3Manager, S3ManagerSettings
from overhave.utils import get_current_time


@pytest.fixture()
def test_s3_enabled(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return cast(bool, request.param)
    raise NotImplementedError


@pytest.fixture()
def test_s3_autocreate_buckets(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return cast(bool, request.param)
    raise NotImplementedError


@pytest.fixture()
def test_s3_manager_settings(
    test_s3_enabled: bool, test_s3_autocreate_buckets: bool, faker: Faker
) -> S3ManagerSettings:
    return S3ManagerSettings(
        enabled=test_s3_enabled,
        url="https://overhave.readthedocs.io",
        access_key=faker.word(),
        secret_key=faker.word(),
        autocreate_buckets=test_s3_autocreate_buckets,
    )


@pytest.fixture()
def test_side_effect(request: FixtureRequest) -> Optional[Exception]:
    if hasattr(request, "param"):
        return cast(Exception, request.param)
    return None


@pytest.fixture()
def test_exception(request: FixtureRequest) -> Optional[Exception]:
    if hasattr(request, "param"):
        return cast(Exception, request.param)
    return None


@pytest.fixture()
def mocked_boto3_client() -> mock.MagicMock:
    mocked_client = mock.MagicMock()
    mocked_client.list_buckets.return_value = {"Buckets": []}
    return mocked_client


@pytest.fixture()
def mocked_boto3_client_getter(
    mocked_boto3_client: mock.MagicMock, test_side_effect: Optional[Exception]
) -> mock.MagicMock:
    with mock.patch("boto3.client", return_value=mocked_boto3_client) as mocked_func:
        if test_side_effect is not None:
            mocked_func.side_effect = test_side_effect
        yield mocked_func


@pytest.fixture()
def test_s3_manager(test_s3_manager_settings: S3ManagerSettings, mocked_boto3_client_getter) -> S3Manager:
    return S3Manager(test_s3_manager_settings)


@pytest.fixture()
def test_bucket_name(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_bucket_creation_date() -> datetime:
    return get_current_time()
