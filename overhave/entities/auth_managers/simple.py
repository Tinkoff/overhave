import logging

from pydantic import SecretStr

from overhave import db
from overhave.entities.auth_managers.secret_mixin import AdminSecretMixin
from overhave.storage import SystemUserModel

logger = logging.getLogger(__name__)


class BaseSimpleAdminAuthorizationManagerException(Exception):
    """Base exception for :class:`SimpleAdminAuthorizationManager`."""


class NullablePasswordError(Exception):
    """Exception for situation when row is without password."""


class SimpleAdminAuthorizationManager(AdminSecretMixin):
    """Class for user registration.

    Manager does not provide real auth_managers. Each user could use preferred name.
    This name will be used for user authority. Each user is unique. Passwords not required.
    """

    def authorize_user(self, username: str, password: SecretStr) -> SystemUserModel | None:
        with db.create_session() as session:
            user = self._system_user_storage.get_user_by_credits(session=session, login=username)
            if user is None:
                user = self._system_user_storage.create_user(session=session, login=username, password=password)
            if user.password is None:
                raise NullablePasswordError(f"User with id={user.id} has not got password!")
            if user.password == password.get_secret_value():
                return SystemUserModel.model_validate(user)
        return None
