import logging
from typing import cast

from flask import redirect
from flask_login import LoginManager
from werkzeug import Response

from overhave import db

logger = logging.getLogger(__name__)


def _load_user(user_id: int) -> db.BaseUser:
    """Return user for overlord. """
    logger.info('Get user %s', user_id)
    with db.create_session(expire_on_commit=False) as s:
        return cast(db.BaseUser, s.query(db.UserRole).filter(db.UserRole.id == user_id).first())


def _unathorized_response() -> Response:
    return redirect('/login')


def get_flask_login_manager() -> LoginManager:
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.user_loader(_load_user)
    login_manager.unauthorized_handler(_unathorized_response)
    return login_manager
