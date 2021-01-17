from typing import Any

import flask
from flask import redirect, request, url_for
from flask_login import current_user
from wtforms import PasswordField

from overhave import db
from overhave.admin.views.base import ModelViewConfigured


class AccessModelView(ModelViewConfigured):
    """ Additional base view for access views. """

    can_view_details = False

    form_overrides = dict(password=PasswordField)

    def is_accessible(self) -> bool:
        return bool(current_user.is_authenticated and current_user.role == db.Role.admin)

    def inaccessible_callback(self, name: str, **kwargs: Any) -> Any:
        # redirect to login page if user doesn't have access
        if current_user.is_authenticated:
            flask.flash("You have not got access for users and groups management!", category="error")
            return redirect(url_for('admin.index'))
        return redirect(url_for('admin.login', next=request.url))


class UserView(AccessModelView):
    """ View for application user access management. """

    column_list = ['id', 'login', 'role', 'created_at']
    column_searchable_list = ['login']


class GroupView(AccessModelView):
    """ View for application group access management. """

    column_searchable_list = ['group']
