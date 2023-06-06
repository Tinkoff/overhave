from pathlib import Path

import allure
import allure_commons.types

from overhave.scenario import OverhaveProjectSettings
from overhave.test_execution import OverhaveAdminLinkSettings


def add_task_links_to_report(project_settings: OverhaveProjectSettings, tasks: list[str]) -> None:
    for task in tasks:
        allure.dynamic.link(
            url=str(project_settings.get_task_link(task)), link_type=allure_commons.types.LinkType.LINK, name=task
        )


def add_git_project_feature_link_to_report(project_settings: OverhaveProjectSettings, filepath: Path) -> None:
    allure.dynamic.link(
        url=str(project_settings.get_git_feature_url(filepath)),
        link_type=allure_commons.types.LinkType.TEST_CASE,
        name=filepath.as_posix(),
    )


def add_admin_feature_link_to_report(admin_link_settings: OverhaveAdminLinkSettings, feature_id: int) -> None:
    allure.dynamic.link(
        url=str(admin_link_settings.get_feature_url(feature_id)),
        link_type=allure_commons.types.LinkType.TEST_CASE,
        name=admin_link_settings.get_feature_link_name(feature_id),
    )
