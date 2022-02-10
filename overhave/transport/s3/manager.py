import logging
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import boto3
import botocore.exceptions
import urllib3
from boto3_type_annotations.s3 import Client
from pydantic.tools import parse_obj_as
from yarl import URL

from overhave.transport.s3.models import BucketModel, DeletionResultModel, ObjectModel
from overhave.transport.s3.objects import OverhaveS3Bucket
from overhave.transport.s3.settings import OverhaveS3ManagerSettings
from overhave.utils import make_url

logger = logging.getLogger(__name__)


class BaseS3ManagerException(Exception):
    """Base exception for :class:`S3Manager`."""


class UndefinedClientException(BaseS3ManagerException):
    """Exception for situation with not initialized client in :class:`S3Manager`."""


class InvalidEndpointError(BaseS3ManagerException):
    """Exception for ValueError with invalid endpoint from boto3."""


class InvalidCredentialsError(BaseS3ManagerException):
    """Exception for situation with invalid credentials from boto3."""


class EndpointConnectionError(BaseS3ManagerException):
    """Exception for situation with endpoint connection error from boto3."""


class ClientError(BaseS3ManagerException):
    """Exception for situation with client error from boto3."""


class EmptyObjectsListError(BaseS3ManagerException):
    """Exception for situation with empty object list."""


def _s3_error(msg: str):  # type: ignore
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Dict[str, Any]) -> Any:
            try:
                return func(*args, **kwargs)
            except botocore.exceptions.ClientError as e:
                raise ClientError(msg) from e

        return wrapper

    return decorator


class S3Manager:
    """Class for s3 management with boto3 client."""

    def __init__(self, settings: OverhaveS3ManagerSettings):
        self._settings = settings
        self._client: Optional[Client] = None

    def initialize(self) -> None:
        if not self._settings.enabled:
            logger.info("S3Manager disabled and has not been initialized.")
            return
        self._client = self._get_client(self._settings)
        if self._settings.autocreate_buckets:
            self._ensure_buckets_exists()

    @property
    def enabled(self) -> bool:
        return self._client is not None

    @staticmethod
    def _get_client(settings: OverhaveS3ManagerSettings) -> Client:
        if not settings.verify:
            logger.warning("Verification disabled in '%s', so ignore 'urllib3' warnings.", type(settings).__name__)
            urllib3.disable_warnings()
        try:
            client = boto3.client(
                "s3",
                region_name=settings.region_name,
                verify=settings.verify,
                endpoint_url=settings.url,
                aws_access_key_id=settings.access_key,
                aws_secret_access_key=settings.secret_key,
            )
            logger.info("s3 client successfully initialized.")
            return client  # noqa: R504
        except ValueError as e:
            raise InvalidEndpointError("Incorrect specified URL for s3 client!") from e
        except botocore.exceptions.ClientError as e:
            raise InvalidCredentialsError("Invalid credentials for s3 client!") from e
        except botocore.exceptions.EndpointConnectionError as e:
            raise EndpointConnectionError(f"Could not connect to '{settings.url}'!") from e

    @property
    def _ensured_client(self) -> Client:
        if self._client is None:
            raise UndefinedClientException("s3 client has not been initialized!")
        return self._client

    def _ensure_buckets_exists(self) -> None:
        remote_buckets = self._get_buckets()
        logger.info("Existing remote s3 buckets: %s", remote_buckets)
        bucket_names = [model.name for model in remote_buckets]
        for bucket in list(filter(lambda x: x.value not in bucket_names, OverhaveS3Bucket)):
            self.create_bucket(bucket.value)
        logger.info("Successfully ensured existence of Overhave service buckets.")

    @_s3_error(msg="Error while getting buckets list!")
    def _get_buckets(self) -> List[BucketModel]:
        response = self._ensured_client.list_buckets()
        return parse_obj_as(List[BucketModel], response.get("Buckets"))

    @_s3_error(msg="Error while creating bucket!")
    def create_bucket(self, bucket: str) -> None:
        logger.info("Creating bucket %s...", bucket)
        kwargs: Dict[str, Any] = {"Bucket": bucket}
        if isinstance(self._settings.region_name, str):
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": self._settings.region_name}
        self._ensured_client.create_bucket(**kwargs)
        logger.info("Bucket %s successfully created.", bucket)

    def upload_file(self, file: Path, bucket: OverhaveS3Bucket) -> bool:
        logger.info("Start uploading file '%s'...", file.name)
        try:
            self._ensured_client.upload_file(file.as_posix(), bucket.value, file.name)
            logger.info("File '%s' successfully uploaded", file.name)
            return True
        except botocore.exceptions.ClientError:
            logger.exception("Could not upload file to s3 cloud!")
            return False

    @_s3_error(msg="Error while getting bucket objects list!")
    def get_bucket_objects(self, bucket: str) -> List[ObjectModel]:
        response = self._ensured_client.list_objects(Bucket=bucket)
        logger.debug("List objects response:\n%s", response)
        return parse_obj_as(List[ObjectModel], response.get("Contents"))

    @_s3_error(msg="Error while deleting bucket objects!")
    def delete_bucket_objects(self, bucket: str, objects: List[ObjectModel]) -> DeletionResultModel:
        if not objects:
            raise EmptyObjectsListError("No one object specified for deletion!")
        logger.info("Deleting items %s...", [obj.name for obj in objects])
        response = self._ensured_client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": obj.name} for obj in objects]},
        )
        logger.debug("Delete objects response:\n%s", response)
        return DeletionResultModel.parse_obj(response)

    def _ensure_bucket_clean(self, bucket: str) -> None:
        objects = self.get_bucket_objects(bucket)
        if not objects:
            logger.info("Has not got any objects in bucket '%s'.", bucket)
            return
        deletion_result = self.delete_bucket_objects(bucket=bucket, objects=objects)
        if len(deletion_result.deleted) != len(objects):
            logger.warning("Expected %s deleted objects, got %s!", len(objects), len(deletion_result.deleted))
            logger.warning("Errors while deleted items:\n%s", deletion_result.errors)
        logger.info("Items %s successfully deleted.", [obj.name for obj in deletion_result.deleted])

    @_s3_error("Error while deleting bucket!")
    def delete_bucket(self, bucket: str, force: bool = False) -> None:
        if force:
            self._ensure_bucket_clean(bucket)
        logger.info("Deleting bucket '%s'...", bucket)
        self._ensured_client.delete_bucket(Bucket=bucket)
        logger.info("Bucket '%s' successfully deleted.", bucket)

    def download_file(self, filename: str, dir_to_save: Path, bucket: str) -> bool:
        logger.info("Start downloading file '%s'...", filename)
        try:
            self._ensured_client.download_file(
                Bucket=bucket, Key=filename, Filename=(dir_to_save / filename).as_posix()
            )
            logger.info("File '%s' successfully downloaded", filename)
            return True
        except botocore.exceptions.ClientError:
            logger.exception("Could not download file from s3 cloud!")
            return False

    def create_presigned_url(self, bucket: str, object_name: str, expiration: timedelta) -> Optional[URL]:
        try:
            response = self._ensured_client.generate_presigned_url(
                "get_object", Params={"Bucket": bucket, "Key": object_name}, ExpiresIn=int(expiration.total_seconds())
            )
            logger.info("Created presigned URL: '%s'", response)
            return make_url(response)
        except botocore.exceptions.ClientError:
            logging.exception("Could not create presigned URL for s3 cloud object '%s'!", object_name)
            return None
