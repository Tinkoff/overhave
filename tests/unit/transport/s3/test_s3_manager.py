import pytest

from overhave.transport import S3Manager


class TestS3Manager:
    """ Unit tests for :class:`S3Manager`. """

    @pytest.mark.parametrize("test_s3_enabled", [False], indirect=True)
    def test_initialize_disabled(self, test_s3_manager: S3Manager):
        test_s3_manager.initialize()
        assert test_s3_manager._client is None

    @pytest.mark.parametrize("test_s3_enabled", [True], indirect=True)
    def test_initialize_enabled(self, test_s3_manager: S3Manager):
        test_s3_manager.initialize()
        assert test_s3_manager._client
