import datetime
from typing import Any, List, Optional

from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup


def datetime_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    time: Optional[datetime.datetime] = getattr(model, name)
    if time:
        return Markup(time.isoformat(sep=' ', timespec='seconds'))
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


def result_report_formatter(view: ModelView, context: Any, model: Any, name: str) -> Markup:
    status = getattr(model, name)
    if not status:
        return Markup("")
    report_link = getattr(model, 'report')
    if not report_link:
        return Markup(f"{status}")
    return Markup(
        f"<form action='/reports/{ report_link }' target='_blank'>"
        "<fieldset title='Go to Allure report'>"
        f"<button class='link-button'>{status}</button>"
        "</fieldset>"
        "</form>"
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
