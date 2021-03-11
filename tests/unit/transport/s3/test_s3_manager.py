from pathlib import Path
from typing import Any, Dict
from unittest import mock

import botocore.exceptions
import pytest

from overhave.transport import OverhaveS3Bucket, S3Manager, S3ManagerSettings
from overhave.transport.s3.manager import (
    EmptyObjectsListError,
    EndpointConnectionError,
    InvalidCredentialsError,
    InvalidEndpointError,
)
from overhave.transport.s3.models import ObjectModel


@pytest.mark.parametrize("test_s3_autocreate_buckets", [False, True], indirect=True)
class TestS3Manager:
    """ Unit tests for :class:`S3Manager` with non-bucket defs. """

    @pytest.mark.parametrize("test_s3_enabled", [False], indirect=True)
    def test_initialize_disabled(self, mocked_boto3_client_getter, test_s3_manager: S3Manager):
        test_s3_manager.initialize()
        mocked_boto3_client_getter.assert_not_called()
        assert test_s3_manager._client is None

    @pytest.mark.parametrize("test_s3_enabled", [True], indirect=True)
    def test_initialize_enabled(
        self,
        mocked_boto3_client_getter: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_s3_manager: S3Manager,
    ):
        test_s3_manager.initialize()
        mocked_boto3_client_getter.assert_called_once_with(
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
    def test_initialize_errors(self, test_exception: Exception, mocked_boto3_client_getter, test_s3_manager: S3Manager):
        with pytest.raises(type(test_exception)):
            test_s3_manager.initialize()
        mocked_boto3_client_getter.assert_called_once()


@pytest.mark.parametrize("test_s3_autocreate_buckets", [False, True], indirect=True)
@pytest.mark.parametrize("test_s3_enabled", [True], indirect=True)
@pytest.mark.parametrize("bucket", list(OverhaveS3Bucket))
class TestInitializedS3Manager:
    """ Unit tests for initialized :class:`S3Manager`. """

    def test_create_bucket(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
    ):
        test_initialized_s3_manager.create_bucket(bucket.value)
        mocked_boto3_client.create_bucket.assert_called()

    def test_get_bucket_objects(
        self,
        test_object_dict: Dict[str, Any],
        mocked_boto3_client: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
    ):
        objects = test_initialized_s3_manager.get_bucket_objects(bucket.value)
        mocked_boto3_client.list_objects.assert_called_once_with(Bucket=bucket.value)
        assert objects == [ObjectModel.parse_obj(test_object_dict)]

    def test_upload_file(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
        tmp_path: Path,
    ):
        assert test_initialized_s3_manager.upload_file(tmp_path, bucket=bucket)
        mocked_boto3_client.upload_file.assert_called_once_with(tmp_path.as_posix(), bucket.value, tmp_path.name)

    def test_error_when_upload_file(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
        tmp_path: Path,
        caplog,
    ):
        mocked_boto3_client.upload_file.side_effect = botocore.exceptions.ClientError(
            mock.MagicMock(), mock.MagicMock()
        )
        assert not test_initialized_s3_manager.upload_file(tmp_path, bucket=bucket)
        assert "Could not upload file to s3 cloud!" in caplog.text

    def test_delete_files(
        self,
        test_object_dict: Dict[str, Any],
        mocked_boto3_client: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
    ):
        objects = [ObjectModel.parse_obj(test_object_dict)]
        test_initialized_s3_manager.delete_bucket_objects(bucket=bucket.value, objects=objects)
        mocked_boto3_client.delete_objects.assert_called_once_with(
            Bucket=bucket, Delete={"Objects": [{"Key": obj.name} for obj in objects]}
        )

    def test_delete_files_empty_error(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
    ):
        with pytest.raises(EmptyObjectsListError):
            test_initialized_s3_manager.delete_bucket_objects(bucket=bucket.value, objects=[])
        mocked_boto3_client.delete_objects.assert_not_called()

    @pytest.mark.parametrize("force", [False, True])
    def test_delete_bucket(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_s3_manager_settings: S3ManagerSettings,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
        force: bool,
    ):
        test_initialized_s3_manager.delete_bucket(bucket.value, force=force)
        if force:
            mocked_boto3_client.list_objects.assert_called_once_with(Bucket=bucket.value)
            mocked_boto3_client.delete_objects.assert_called_once()
        else:
            mocked_boto3_client.list_objects.assert_not_called()
            mocked_boto3_client.delete_objects.assert_not_called()
        mocked_boto3_client.delete_bucket.assert_called_once_with(Bucket=bucket.value)

    def test_download_file(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
        tmp_path: Path,
        test_filename: str,
    ):
        assert test_initialized_s3_manager.download_file(filename=test_filename, dir_to_save=tmp_path, bucket=bucket)
        mocked_boto3_client.download_file.assert_called_once_with(
            Bucket=bucket, Key=test_filename, Filename=(tmp_path / test_filename).as_posix()
        )

    def test_error_when_download_file(
        self,
        mocked_boto3_client: mock.MagicMock,
        test_initialized_s3_manager: S3Manager,
        bucket: OverhaveS3Bucket,
        tmp_path: Path,
        test_filename: str,
        caplog,
    ):
        mocked_boto3_client.download_file.side_effect = botocore.exceptions.ClientError(
            mock.MagicMock(), mock.MagicMock()
        )
        assert not test_initialized_s3_manager.download_file(
            filename=test_filename, dir_to_save=tmp_path, bucket=bucket
        )
        assert "Could not download file from s3 cloud!" in caplog.text
