from typing import Any

from flask import redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from overhave.admin.views.formatters import datetime_formatter, task_formatter


class ModelViewConfigured(ModelView):
    """ Base model view. """

    column_default_sort = ('id', True)
    column_display_pk = True
    can_view_details = True
    page_size = 100
    simple_list_pager = True

    column_exclude_list = ('meta',)
    column_labels = dict(
        user='Author',
        name="Name",
        feature_type="Type",
        task="Tasks",
        last_edited_by="Editor",
        released="Published",
        created_at="Creation time",
        scenario="Scenario",
        start="Start time",
        end="Finish time",
        executed_by="Initiator",
        status="Status",
        report="Report",
        traceback="Error traceback",
        feature_id="Feature ID",
        test_run_id="Test run ID",
        pr_url="Pull-request URL / Traceback",
    )
    column_formatters = dict(
        created_at=datetime_formatter, start=datetime_formatter, end=datetime_formatter, task=task_formatter,
    )
    column_descriptions = dict(
        name="Feature header for business scenarios",
        feature_type="Type of scenarios set",
        task="Tracker tasks converted to web links when viewed",
        last_edited_by="Last editor of scenarios set",
        user="Author of scenarios set",
        released="Features repository publishing status",
        executed_by="Initiator of scenarios set test run",
        status="Result scenarios set test run",
    )

    def is_accessible(self) -> Any:
        return current_user.is_authenticated

    def inaccessible_callback(self, name: str, **kwargs: Any) -> Any:
        # redirect to login page if user doesn't have access
        return redirect(url_for('admin.login', next=request.url))


class ModelViewProtected(ModelViewConfigured):
    """ Protected view. """

    can_delete = False
    can_edit = False
    can_create = False
