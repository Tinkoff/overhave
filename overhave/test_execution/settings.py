from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Type

from pydantic import BaseModel, validator
from yarl import URL

from overhave.base_settings import BaseOverhavePrefix
from overhave.utils import make_url


class EmptyOverhaveAdminURLError(ValueError):
    """Exception for situation with empty ````admin_url``` while trying to ```get_feature_url```."""


class EmptyTaskTrackerURLError(ValueError):
    """Exception for situation with empty ```task_tracker_url``` while trying to ```get_task_link```."""


class EmptyGitProjectURLError(ValueError):
    """Exception for situation with empty ```git_project_url``` while trying to ```get_git_feature_url```."""


class OverhaveAdminLinkSettings(BaseOverhavePrefix):
    """Settings for dynamic links to Overhave Admin in Allure report."""

    admin_url: Optional[URL]

    feature_id_filter_path: str = "feature/?flt2_0={feature_id}"
    feature_id_placeholder: str = "Overhave feature #{feature_id}"

    @validator("admin_url", pre=True)
    def make_admin_url(cls, v: Optional[str]) -> Optional[URL]:
        return make_url(v)

    @property
    def enabled(self) -> bool:
        return self.admin_url is not None

    def get_feature_url(self, feature_id: int) -> str:
        if isinstance(self.admin_url, URL):
            return self.admin_url.human_repr() + f"/{self.feature_id_filter_path.format(feature_id=feature_id)}"
        raise EmptyOverhaveAdminURLError("Overhave admin URL is None, so could not create link URL!")

    def get_feature_link_name(self, feature_id: int) -> str:
        return self.feature_id_placeholder.format(feature_id=feature_id)


class OverhaveProjectSettings(BaseOverhavePrefix):
    """
    Entity project settings.

    You could specify your fixture content for specific pytest usage with your own plugins.
    It could give you pretty extended file with powerful possibilities.
    `fixture_context` will be formatted by `OverhaveProccessor` before test would be started.
    """

    # Fixture content in list format, which would be compiled into formatted string.
    fixture_content: List[str] = [
        "from pytest_bdd import scenarios",
        "from overhave import overhave_proxy_manager",
        "pytest_plugins = overhave_proxy_manager().plugin_resolver.get_plugins()",
        "scenarios('{feature_file_path}')",
    ]

    # Task tracker URL
    task_tracker_url: Optional[URL]
    # Behaviour specification keyword for tasks attachment
    tasks_keyword: Optional[str]

    # Git project URL
    git_project_url: Optional[URL]

    # Templates are used for creation of test user and system specifications.
    # Keys for specification mapping are still the same - feature types.
    user_spec_template_mapping: Mapping[str, Type[BaseModel]] = {}

    @validator("task_tracker_url", pre=True)
    def make_tasktracker_url(cls, v: Optional[str]) -> Optional[URL]:
        return make_url(v)

    @validator("tasks_keyword")
    def validate_links_keyword(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if isinstance(v, str) and values.get("task_tracker_url") is None:
            raise ValueError("Task tracker URL should be specified in case of links keyword usage!")
        return v

    @validator("git_project_url", pre=True)
    def make_git_project_url(cls, v: Optional[str]) -> Optional[URL]:
        return make_url(v)

    def get_task_link(self, link: str) -> URL:
        if isinstance(self.task_tracker_url, URL):
            return self.task_tracker_url / link
        raise EmptyTaskTrackerURLError("Task tracker URL is None, so could not create link URL!")

    def get_git_feature_url(self, filepath: Path) -> URL:
        if isinstance(self.git_project_url, URL):
            return self.git_project_url / filepath.as_posix()
        raise EmptyGitProjectURLError("Git project URL is None, so could not create link URL!")


class OverhaveTestSettings(BaseOverhavePrefix):
    """Settings for PytestRunner, which runs scenario tests with specified addoptions."""

    default_pytest_addoptions: str = "--disable-warnings"
    extra_pytest_addoptions: Optional[str]

    workers: Optional[int]  # Number of xdist workers, `None` by default
