import logging
from typing import Optional

from flask import redirect
from flask_login import LoginManager
from werkzeug import Response

from overhave.entities import SystemUserModel
from overhave.storage import ISystemUserStorage

logger = logging.getLogger(__name__)


class FlaskLoginManager(LoginManager):
    """Custom Flask LoginManager for user acknowledgement."""

    def __init__(self, system_user_storage: ISystemUserStorage, login_view: str) -> None:
        super().__init__()
        self.login_view = login_view
        self.user_loader(self._get_user)
        self.unauthorized_handler(self._unathorized_response)

        self._system_user_storage = system_user_storage

    def _get_user(self, user_id: int) -> Optional[SystemUserModel]:
        logger.info("Get user by id=%s...", user_id)
        return self._system_user_storage.get_user(user_id=user_id)

    def _unathorized_response(self) -> Response:
        return redirect(f"/{self.login_view}")
