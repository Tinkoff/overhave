import datetime
from typing import Any, List, Optional, Union

from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from yarl import URL

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus


def datetime_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    time: Optional[datetime.datetime] = getattr(model, name)
    if time:
        return Markup(time.strftime("%d-%m-%Y %H:%M:%S"))
    return Markup("")


def task_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    tasks = getattr(model, name)
    browse_url = getattr(view, "browse_url")
    if not tasks:
        return Markup("")
    if not browse_url:
        return Markup(", ".join(tasks))
    task_links: List[str] = []
    for task in tasks:
        task_links.append(f"<a href='{browse_url}/{task}' target='blank'>{task}</a>")
    return Markup(", ".join(task_links))


def _get_button_class_by_status(status: str) -> str:
    enum_member = TestRunStatus[status]
    if enum_member is TestRunStatus.SUCCESS:
        return "success-btn"
    return "default-btn"


def _get_testrun_details_link(test_run_id: Union[int, str]) -> str:
    return f"href='/testrun/details/?id={test_run_id}'"


def result_report_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    status = getattr(model, name)
    if not status:
        return Markup("")

    report_status = TestReportStatus[getattr(model, "report_status")]
    if report_status.has_report:
        action = f"href='/reports/{getattr(model, 'report')}' target='_blank'"
        title = "Go to report"
    else:
        action = _get_testrun_details_link(model.id)
        title = "Show details"

    return Markup(
        f"<a {action}"
        f"<form action='#'>"
        f"<fieldset title='{title}'>"
        f"<button class='link-button {_get_button_class_by_status(status)}'>{status}</button>"
        "</fieldset>"
        "</form>"
        "</a>"
    )


def json_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    data = getattr(model, name)
    if not data:
        return Markup("")
    info = ""
    for key, value in data.items():
        if value:
            info += f"<b>{key}</b>:&nbsp;&nbsp;{value}<br>"
    return Markup("<form>" "<fieldset>" f"<div class='json-data'>{info}</div>" "</fieldset>" "</form>")


def _get_feature_link_markup(feature_id: Union[int, str], feature_name: str) -> Markup:
    return Markup(f"<a href='/feature/edit/?id={feature_id}'>{feature_name}</a>")


def feature_link_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    name = getattr(model, name, None)
    if not name:
        return Markup("")
    if isinstance(model, db.Feature):
        return _get_feature_link_markup(feature_id=model.id, feature_name=name)
    if isinstance(model, db.TestRun):
        return _get_feature_link_markup(feature_id=model.scenario.feature_id, feature_name=name)
    if isinstance(model, db.Draft):
        return _get_feature_link_markup(feature_id=model.feature_id, feature_name=model.feature.name)
    return Markup(name)


def draft_testrun_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    test_run = getattr(model, name)
    if not test_run:
        return Markup("")
    return Markup(f"<a {_get_testrun_details_link(test_run)}>{test_run}</a>")


def draft_prurl_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    pr_url = getattr(model, name)
    if not pr_url or pr_url == "None":
        return Markup("")
    return Markup(f"<a href='{URL(pr_url).human_repr()}'>{pr_url}</a>")
