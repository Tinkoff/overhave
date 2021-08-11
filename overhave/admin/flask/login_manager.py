import logging
from typing import Optional

from flask import redirect
from flask_login import LoginManager
from werkzeug import Response

from overhave.entities import SystemUserModel
from overhave.storage import SystemUserStorage

logger = logging.getLogger(__name__)


def _load_user(user_id: int) -> Optional[SystemUserModel]:
    logger.info("Get user by id=%s...", user_id)
    return SystemUserStorage().get_user(user_id=user_id)


def _unathorized_response() -> Response:
    return redirect("/login")


def get_flask_login_manager() -> LoginManager:
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.user_loader(_load_user)
    login_manager.unauthorized_handler(_unathorized_response)
    return login_manager
