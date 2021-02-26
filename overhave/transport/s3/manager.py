import logging
from functools import cached_property

import boto3
import urllib3
from boto3_type_annotations.s3 import Client

from overhave.transport.s3.models import BucketsListModel
from overhave.transport.s3.objects import OverhaveS3Bucket
from overhave.transport.s3.settings import S3ClientSettings

logger = logging.getLogger(__name__)


class S3Manager:
    """ Class for s3 management with boto3 client. """

    def __init__(self, settings: S3ClientSettings):
        self._settings = settings

    @cached_property
    def _client(self) -> Client:
        if not self._settings.verify:
            logger.warning(
                "Verification disabled in '%s', so ignore 'urllib3' warnings.", type(self._settings).__name__
            )
            urllib3.disable_warnings()
        client = boto3.client(
            "s3",
            region_name=self._settings.region_name,
            verify=self._settings.verify,
            endpoint_url=self._settings.url.human_repr(),
            aws_access_key_id=self._settings.access_key,
            aws_secret_access_key=self._settings.secret_key,
        )
        logger.info("s3 client successfully initialized.")
        return client  # noqa: R504

    def _ensure_buckets_exists(self) -> None:
        remote_buckets = self._get_buckets()
        logger.info("Existing remote s3 buckets: %s", remote_buckets.items)
        bucket_names = [model.name for model in remote_buckets.items]
        for bucket in list(filter(lambda x: x.value not in bucket_names, OverhaveS3Bucket)):
            self._create_bucket(bucket)
        logger.info("Successfully ensured existence of Overhave service buckets.")

    def _get_buckets(self) -> BucketsListModel:
        return BucketsListModel.parse_obj(self._client.list_buckets().get("Buckets"))

    def _create_bucket(self, bucket: OverhaveS3Bucket) -> None:
        logger.info("Creating bucket %s...", bucket)
        kwargs = {"Bucket": bucket.value}
        if isinstance(self._settings.region_name, str):
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": self._settings.region_name}
        self._client.create_bucket(**kwargs)
        logger.info("Bucket %s successfully created.", bucket)
