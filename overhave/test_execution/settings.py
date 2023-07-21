import httpx
from pydantic import Field, field_validator

from overhave.base_settings import BaseOverhavePrefix
from overhave.utils import make_url


class EmptyOverhaveAdminURLError(ValueError):
    """Exception for situation with empty ````admin_url``` while trying to ```get_feature_url```."""


class OverhaveAdminLinkSettings(BaseOverhavePrefix):
    """Settings for dynamic links to Overhave Admin in Allure report."""

    admin_url: httpx.URL | None

    feature_id_filter_path: str = "feature/?flt2_0={feature_id}"
    feature_id_placeholder: str = "Overhave feature #{feature_id}"

    @field_validator("admin_url", mode="before")
    def make_admin_url(cls, v: str | None) -> httpx.URL | None:
        return make_url(v)

    @property
    def enabled(self) -> bool:
        return self.admin_url is not None

    def get_feature_url(self, feature_id: int) -> httpx.URL:
        if isinstance(self.admin_url, httpx.URL):
            return httpx.URL(f"{self.admin_url}/{self.feature_id_filter_path.format(feature_id=feature_id)}")
        raise EmptyOverhaveAdminURLError("Overhave admin URL is None, so could not create link URL!")

    def get_feature_link_name(self, feature_id: int) -> str:
        return self.feature_id_placeholder.format(feature_id=feature_id)


class OverhaveTestSettings(BaseOverhavePrefix):
    """Settings for PytestRunner, which runs scenario tests with specified addoptions."""

    default_pytest_addoptions: str = "--disable-warnings"
    extra_pytest_addoptions: str | None = Field(default=None)

    workers: int | None = Field(default=None, description="Number of xdist workers")


class OverhaveStepCollectorSettings(BaseOverhavePrefix):
    """Settings for StepCollector, which collect BDD steps for Overhave Admin UI."""

    hide_non_public_steps: bool = False
