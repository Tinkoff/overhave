from typing import Any, cast

from flask import redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from overhave.admin.views.formatters.formatters import (
    datetime_formatter,
    draft_feature_formatter,
    draft_prurl_formatter,
    draft_testrun_formatter,
    feature_link_formatter,
    file_path_formatter,
    json_formatter,
    result_report_formatter,
    task_formatter,
)


class ModelViewConfigured(ModelView):
    """ Base model view. """

    column_default_sort = ("id", True)
    column_display_pk = True
    can_view_details = True
    page_size = 100
    simple_list_pager = True

    column_exclude_list = ("meta",)
    column_labels = {
        "user": "Author",
        "name": "Name",
        "feature_type": "Type",
        "task": "Tasks",
        "last_edited_by": "Editor",
        "released": "Published",
        "created_at": "Creation time",
        "scenario": "Scenario",
        "start": "Start time",
        "end": "Finish time",
        "executed_by": "Initiator",
        "status": "Status",
        "report": "Report",
        "traceback": "Error traceback",
        "feature_id": "Feature",
        "test_run_id": "Test run ID",
        "pr_url": "Pull-request URL",
        "initiated_by": "Initiator",
        "published_by": "Publisher",
    }
    column_formatters = {
        "created_at": datetime_formatter,
        "start": datetime_formatter,
        "end": datetime_formatter,
        "task": task_formatter,
        "status": result_report_formatter,
        "specification": json_formatter,
        "name": feature_link_formatter,
        "feature_id": draft_feature_formatter,
        "test_run_id": draft_testrun_formatter,
        "pr_url": draft_prurl_formatter,
        "file_path": file_path_formatter,
    }
    column_descriptions = dict(
        name="Feature header for business scenarios",
        task="Tracker tasks converted to web links when viewed",
        last_edited_by="Last editor of scenarios set",
        author="Author of scenarios set",
        released="Feature's last version publishing status",
        executed_by="Initiator of scenarios set test run",
        status="Test run result",
    )

    def is_accessible(self) -> Any:
        return current_user.is_authenticated

    def inaccessible_callback(self, name: str, **kwargs: Any) -> Any:
        # redirect to login page if user doesn't have access
        return redirect(url_for("admin.login", next=request.url))

    @property
    def current_user(self) -> str:
        return cast(str, current_user.login)


class ModelViewProtected(ModelViewConfigured):
    """ Protected view. """

    can_delete = False
    can_edit = False
    can_create = False
