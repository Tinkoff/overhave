import datetime
from typing import Any, List, Optional

from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup

from overhave.db import TestReportStatus, TestRunStatus


def datetime_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    time: Optional[datetime.datetime] = getattr(model, name)
    if time:
        return Markup(time.strftime('%d-%m-%Y %H:%M:%S'))
    return Markup("")


def task_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    browse_url = getattr(view, 'browse_url')
    tasks = getattr(model, name)
    if not browse_url or not tasks:
        return Markup("")
    task_links: List[str] = []
    for task in tasks:
        task_links.append(f"<a href='{browse_url}/{task}' target='blank'>{task}</a>")
    return Markup(", ".join(task_links))


def _get_button_class_by_status(status: str) -> str:
    enum_member = TestRunStatus[status]
    if enum_member is TestRunStatus.SUCCESS:
        return "success-btn"
    return "default-btn"


def result_report_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    status = getattr(model, name)
    if not status:
        return Markup("")

    report_status = TestReportStatus[getattr(model, 'report_status')]
    if report_status.has_report:
        action = f"href='/reports/{getattr(model, 'report')}' target='_blank'"
        title = "Go to report"
    else:
        action = f"href='/testrun/details/?id={model.id}'"
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
