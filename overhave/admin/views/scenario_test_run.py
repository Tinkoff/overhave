from typing import cast

import werkzeug
from flask_admin import expose
from flask_login import current_user
from wtforms import Form, ValidationError

from overhave import db
from overhave.admin.views.base import ModelViewConfigured
from overhave.admin.views.formatters import result_report_formatter


class TestRunView(ModelViewConfigured):
    """ View for :class:`TestRun` table. """

    list_template = 'test_run_list.html'
    details_template = 'test_run_detail.html'
    can_edit = True
    column_searchable_list = (
        'name',
        'executed_by',
    )
    column_list = (
        'id',
        'name',
        'start',
        'end',
        'executed_by',
        'status',
    )
    column_filters = (
        'name',
        'start',
        'executed_by',
        'status',
    )

    column_formatters = dict(status=result_report_formatter,)

    def on_model_change(self, form: Form, model: db.TestRun, is_created: bool) -> None:
        if not is_created and current_user.role != db.Role.admin:
            raise ValidationError('Only administrator could change test run data!')

    def on_model_delete(self, model: db.TestRun) -> None:
        if not (current_user.login == model.executed_by or current_user.role == db.Role.admin):
            raise ValidationError('Only test run initiator could delete test run result!')

    @expose('/details/', methods=('GET', 'POST'))
    def details_view(self) -> werkzeug.Response:
        return cast(werkzeug.Response, super().details_view())
