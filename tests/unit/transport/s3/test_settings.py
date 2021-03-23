import pytest
from pydantic import ValidationError

from overhave.transport import OverhaveS3ManagerSettings


class TestS3ManagerSettings:
    """ Unit tests for :class:`OverhaveS3ManagerSettings`. """

    @pytest.mark.parametrize("test_s3_enabled", [False])
    def test_disabled(self, test_s3_enabled: bool):
        settings = OverhaveS3ManagerSettings(enabled=test_s3_enabled)
        assert not settings.enabled
        assert not settings.url
        assert not settings.access_key
        assert not settings.secret_key

    @pytest.mark.parametrize("test_s3_enabled", [True])
    def test_empty_enabled(self, test_s3_enabled: bool):
        with pytest.raises(ValidationError):
            OverhaveS3ManagerSettings(enabled=test_s3_enabled)

    @pytest.mark.parametrize("test_s3_autocreate_buckets", [False, True], indirect=True)
    @pytest.mark.parametrize("test_s3_enabled", [True], indirect=True)
    def test_correct_enabled(
        self,
        test_s3_enabled: bool,
        test_s3_autocreate_buckets: bool,
        test_s3_manager_settings: OverhaveS3ManagerSettings,
    ):
        assert test_s3_manager_settings.enabled == test_s3_enabled
        assert test_s3_manager_settings.url
        assert test_s3_manager_settings.access_key
        assert test_s3_manager_settings.secret_key
        assert test_s3_manager_settings.verify
        assert test_s3_manager_settings.autocreate_buckets == test_s3_autocreate_buckets
