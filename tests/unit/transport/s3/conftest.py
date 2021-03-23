from datetime import datetime
from typing import Any, Dict, Optional, cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave.transport import OverhaveS3ManagerSettings, S3Manager
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
) -> OverhaveS3ManagerSettings:
    return OverhaveS3ManagerSettings(
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


@pytest.fixture(scope="class")
def test_object_owner() -> Dict[str, str]:
    return {"DisplayName": "hello-friend", "ID": "hello-friend"}


@pytest.fixture(scope="class")
def test_object_dict(test_object_owner: Dict[str, str]) -> Dict[str, Any]:
    return {
        "Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip",
        "LastModified": datetime(2021, 2, 28, 18, 37, 40, 219000),
        "ETag": '"3b2874d7dceb0f5622fcd5621c8382f2"',
        "Size": 971457,
        "StorageClass": "STANDARD",
        "Owner": test_object_owner,
    }


@pytest.fixture(scope="class")
def test_deletion_result() -> Dict[str, Any]:
    return {
        "ResponseMetadata": {
            "RequestId": "tx000000000000002f6d78a-00603f2f05-3380ab-m1-tst",
            "HostId": "",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "transfer-encoding": "chunked",
                "x-amz-request-id": "tx000000000000002f6d78a-00603f2f05-3380ab-m1-tst",
                "content-type": "application/xml",
                "date": "Wed, 03 Mar 2021 06:39:01 GMT",
            },
            "RetryAttempts": 0,
        },
        "Deleted": [
            {"Key": "576003e4-79f4-11eb-a7ed-acde48001122.zip", "VersionId": '"3b2874d7dceb0f5622fcd5621c8382f2"'},
            {"Key": "d770f754-79f0-11eb-bbe4-acde48001122.zip", "VersionId": '"9d5d01b6328a08d156c18e1b0287d846"'},
        ],
    }


@pytest.fixture()
def mocked_boto3_client(test_object_dict: Dict[str, Any], test_deletion_result: Dict[str, Any]) -> mock.MagicMock:
    mocked_client = mock.MagicMock()
    mocked_client.list_buckets.return_value = {"Buckets": []}
    mocked_client.list_objects.return_value = {"Contents": [test_object_dict]}
    mocked_client.delete_objects.return_value = test_deletion_result
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
def test_s3_manager(test_s3_manager_settings: OverhaveS3ManagerSettings, mocked_boto3_client_getter) -> S3Manager:
    return S3Manager(test_s3_manager_settings)


@pytest.fixture()
def test_initialized_s3_manager(test_s3_manager: S3Manager) -> S3Manager:
    test_s3_manager.initialize()
    return test_s3_manager


@pytest.fixture()
def test_bucket_name(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_bucket_creation_date() -> datetime:
    return get_current_time()


@pytest.fixture()
def test_filename(faker: Faker) -> str:
    return faker.word()
