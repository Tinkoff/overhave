from unittest import mock

import botocore.exceptions
import pytest

from overhave.transport import S3Manager, S3ManagerSettings
from overhave.transport.s3.manager import EndpointConnectionError, InvalidCredentialsError, InvalidEndpointError


class TestS3Manager:
    """ Unit tests for :class:`S3Manager`. """

    @pytest.mark.parametrize("test_s3_enabled", [False], indirect=True)
    def test_initialize_disabled(self, mocked_boto3_client: mock.MagicMock, test_s3_manager: S3Manager):
        test_s3_manager.initialize()
        mocked_boto3_client.assert_not_called()
        assert test_s3_manager._client is None

    @pytest.mark.parametrize("test_s3_enabled", [True], indirect=True)
    def test_initialize_enabled(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_s3_manager: S3Manager,
    ):
        test_s3_manager.initialize()
        mocked_boto3_client.assert_called_once_with(
            "s3",
            region_name=test_s3_manager_settings.region_name,
            verify=test_s3_manager_settings.verify,
            endpoint_url=test_s3_manager_settings.url,
            aws_access_key_id=test_s3_manager_settings.access_key,
            aws_secret_access_key=test_s3_manager_settings.secret_key,
        )
        assert test_s3_manager._client

    @pytest.mark.parametrize("test_s3_enabled", [True], indirect=True)
    @pytest.mark.parametrize(
        ("test_side_effect", "test_exception"),
        [
            (ValueError(), InvalidEndpointError()),
            (botocore.exceptions.ClientError(mock.MagicMock(), mock.MagicMock()), InvalidCredentialsError()),
            (botocore.exceptions.EndpointConnectionError(endpoint_url="uuh"), EndpointConnectionError()),
        ],
        indirect=True,
    )
    def test_initialize_errors(
        self, test_exception: Exception, mocked_boto3_client: mock.MagicMock, test_s3_manager: S3Manager
    ):
        with pytest.raises(type(test_exception)):
            test_s3_manager.initialize()
        mocked_boto3_client.assert_called_once()
