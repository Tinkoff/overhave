import json
import logging
from typing import Optional

import flask
import werkzeug
from flask_admin import expose
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_login import current_user
from wtforms import Form, ValidationError

from overhave import db
from overhave.admin.views.base import ModelViewConfigured
from overhave.factory import proxy_factory
from overhave.redis import EmulationTask
from overhave.redis.objects import EmulationData

logger = logging.getLogger(__name__)


class EmulationView(ModelViewConfigured):
    """ View for :class:`Emulation` table. """

    create_template = 'emulation_create.html'
    edit_template = 'emulation_edit.html'

    can_view_details = False
    column_list = ['id', 'name', 'test_user.feature_type', 'test_user', 'created_by']
    column_searchable_list = ['name', 'created_by']
    form_excluded_columns = ('created_at', 'creator', 'emulation_runs')

    column_labels = {"test_user.feature_type": "Template type"}
    column_descriptions = {
        "name": "Emulation name",
        "test_user.feature_type": "Type of template supported by specified test user",
        "test_user": "Related Test User used for specified emulation",
        "command": "Flags and values for emulation execution",
    }

    @property
    def additional_cmd_description(self) -> Optional[str]:
        return proxy_factory.context.emulation_settings.emulation_desc_link

    def on_model_change(self, form: Form, model: db.Emulation, is_created: bool) -> None:
        if is_created:
            model.created_by = current_user.login

    def on_model_delete(self, model: db.Emulation) -> None:
        if not (current_user.login == model.created_by or current_user.role == db.Role.admin):
            raise ValidationError('Only emulation item creator or administrator could delete it!')

    @staticmethod
    def _run_emulation(emulation_id: int) -> Optional[werkzeug.Response]:
        try:
            emulation_run = proxy_factory.emulation_storage.create_emulation_run(emulation_id)
            proxy_factory.redis_producer.add(EmulationTask(data=EmulationData(emulation_run_id=emulation_run.id)))
            return flask.redirect(flask.url_for("emulationrun.details_view", id=emulation_run.id))
        except Exception as e:
            flask.flash(str(e), category='error')
            return flask.redirect(flask.url_for('emulation.edit_view', id=emulation_id))

    @property
    def description_link(self) -> Optional[str]:
        return proxy_factory.context.emulation_settings.emulation_desc_link

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self) -> Optional[werkzeug.Response]:
        data = flask.request.form
        logger.debug("Request data:\n%s", json.dumps(data))

        rendered: werkzeug.Response = super().edit_view()

        emulation_action = data.get('emulate')
        if not emulation_action:
            logger.debug("Show rendered EditView")
            return rendered
        emulation_id = get_mdict_item_or_list(flask.request.args, 'id')
        if not emulation_id:
            flask.flash("Please, save emulation template before execution")
            return rendered

        logger.debug("Seen emulation request")
        return self._run_emulation(emulation_id)
