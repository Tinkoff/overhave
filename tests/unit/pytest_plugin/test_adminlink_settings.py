from typing import Optional

import pytest
from faker import Faker
from yarl import URL

from overhave import OverhaveAdminLinkSettings
from overhave.pytest_plugin.settings import EmptyOverhaveAdminURLError


@pytest.mark.parametrize("admin_url", [None])
class TestAdminLinkSettingsDisabled:
    """Unit tests for :class:`OverhaveAdminLinkSettings` (disabled)."""

    def test_disabled(self, admin_url: Optional[str], faker: Faker) -> None:
        settings = OverhaveAdminLinkSettings(admin_url=admin_url)
        assert not settings.enabled
        with pytest.raises(EmptyOverhaveAdminURLError):
            assert settings.get_feature_url(faker.random_int())


@pytest.mark.parametrize("admin_url", ["https://overhave.mydomain.com"])
class TestAdminLinkSettings:
    """Unit tests for :class:`OverhaveAdminLinkSettings`."""

    def test_enabled(self, admin_url: str, faker: Faker) -> None:
        settings = OverhaveAdminLinkSettings(admin_url=admin_url)
        assert settings.enabled
        assert isinstance(settings.get_feature_url(faker.random_int()), URL)

    def test_feature_url(self, admin_url: str, faker: Faker) -> None:
        settings = OverhaveAdminLinkSettings(admin_url=admin_url)
        feature_id = faker.random_int()
        assert settings.get_feature_url(feature_id) == URL(admin_url) / settings.feature_id_filter_path.format(
            feature_id=feature_id
        )

    def test_feature_link_name(self, admin_url: str, faker: Faker) -> None:
        settings = OverhaveAdminLinkSettings(admin_url=admin_url)
        feature_id = faker.random_int()
        assert settings.get_feature_link_name(feature_id) == settings.feature_id_placeholder.format(
            feature_id=feature_id
        )
