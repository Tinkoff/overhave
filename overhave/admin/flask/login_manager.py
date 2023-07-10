import logging
from dataclasses import dataclass

from flask import redirect
from flask_login import LoginManager
from werkzeug import Response

from overhave import db
from overhave.storage import ISystemUserStorage, SystemUserModel

logger = logging.getLogger(__name__)


class UnauthorizedUserError(Exception):
    """Raises when user is not authorized and trying to get user fields such as role or login."""


@dataclass(frozen=True)
class AdminPanelUser:
    """SystemUserModel wrapper for flask_login."""

    user_data: SystemUserModel | None

    @property
    def is_authenticated(self) -> bool:
        return self.user_data is not None

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return self.user_data is None

    @property
    def _authorized_user(self) -> SystemUserModel:
        if self.user_data is None:
            raise UnauthorizedUserError("User is not authorized!")
        return self.user_data

    def get_id(self) -> int:
        return self._authorized_user.id

    @property
    def login(self) -> str:
        return self._authorized_user.login

    @property
    def role(self) -> db.Role:
        return self._authorized_user.role

    def __unicode__(self) -> str:
        if self.user_data is not None:
            return self.user_data.login
        return "anonymous"


class FlaskLoginManager(LoginManager):
    """Custom Flask LoginManager for user acknowledgement."""

    def __init__(self, system_user_storage: ISystemUserStorage, login_view: str) -> None:
        super().__init__()
        self.login_view = login_view
        self.user_loader(self._get_user)
        self.unauthorized_handler(self._unathorized_response)

        self._system_user_storage = system_user_storage

    def _get_user(self, user_id: int) -> AdminPanelUser:
        logger.info("Get user by id=%s...", user_id)
        return AdminPanelUser(user_data=self._system_user_storage.get_user_model(user_id=user_id))

    def _unathorized_response(self) -> Response:
        return redirect(f"/{self.login_view}")
