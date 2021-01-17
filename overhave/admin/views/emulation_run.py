import logging
from typing import cast

import werkzeug
from flask_admin import expose
from flask_login import current_user
from wtforms import ValidationError

from overhave import db
from overhave.admin.views.base import ModelViewConfigured

logger = logging.getLogger(__name__)


class EmulationRunView(ModelViewConfigured):
    """ View for :class:`EmulationRun` table. """

    details_template = 'emulation_run_detail.html'

    can_view_details = True
    can_edit = False
    column_list = ('id', 'emulation.name', 'emulation.created_by', 'status', 'created_at')
    column_filters = ('emulation.name', 'emulation.created_by', 'status')
    column_searchable_list = ('emulation.name', 'emulation.created_by')

    column_descriptions = dict(status="Emulation run status")

    def on_model_delete(self, model: db.EmulationRun) -> None:
        if not (current_user.login == model.emulation.created_by or current_user.role == db.Role.admin):
            raise ValidationError('Only test run initiator could delete test run result!')

    @expose('/details/', methods=('GET', 'POST'))
    def details_view(self) -> werkzeug.Response:
        return cast(werkzeug.Response, super().details_view())

    @staticmethod
    def redirect_allowed(model: db.EmulationRun) -> bool:
        return model.port is not None
