import logging
from typing import Any, Callable

import flask
import werkzeug as werkzeug
from flask_admin import expose
from flask_login import current_user
from sqlalchemy.exc import StatementError
from wtforms import Form, ValidationError

from overhave import db
from overhave.admin.views.base import ModelViewConfigured

logger = logging.getLogger(__name__)


def view_wrapper(function_view: Callable[[Any], werkzeug.Response]) -> Callable[[Any], werkzeug.Response]:
    def wrapper(obj: Any) -> werkzeug.Response:
        try:
            return function_view(obj)
        except StatementError:
            flask.flash("Unsupported symbols in tag name!")
            return flask.redirect(flask.request.url)

    return wrapper


class TagsView(ModelViewConfigured):
    """ View for :class:`Feature` table. """

    can_view_details = False

    column_list = (
        "id",
        "value",
        "created_at",
        "created_by",
    )

    form_excluded_columns = ("created_at",)

    def on_model_change(self, form: Form, model: db.Tags, is_created: bool) -> None:
        if not is_created:
            if current_user.login == model.created_by or current_user.role == db.Role.admin:
                return
            raise ValidationError("Only tag creator or administrator could edit it!")
        model.created_by = current_user.login

    def on_model_delete(self, model: db.Tags) -> None:
        if not (current_user.login == model.created_by or current_user.role == db.Role.admin):
            raise ValidationError("Only author or administrator could delete tags!")

    @expose("/edit/", methods=("GET", "POST"))
    @view_wrapper
    def edit_view(self) -> Any:
        return super().edit_view()

    @expose("/new/", methods=("GET", "POST"))
    @view_wrapper
    def crate_view(self) -> Any:
        return super().create_view()
