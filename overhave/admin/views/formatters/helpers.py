from typing import Union

from markupsafe import Markup

from overhave.db import TestRunStatus


def get_button_class_by_status(status: str) -> str:
    enum_member = TestRunStatus[status]
    if enum_member is TestRunStatus.SUCCESS:
        return "success-btn"
    return "default-btn"


def get_testrun_details_link(test_run_id: Union[int, str]) -> str:
    return f"/testrun/details/?id={test_run_id}"


def get_report_index_link(report: str) -> str:
    return f"/reports/{report}/index.html"


def get_feature_link_markup(feature_id: Union[int, str], feature_name: str) -> Markup:
    return Markup(f"<a href='/feature/edit/?id={feature_id}'>{feature_name}</a>")
