import logging
from typing import Optional

from pydantic import SecretStr

from overhave.authorization.manager.secret_mixin import AdminSecretMixin
from overhave.entities import SystemUserModel

logger = logging.getLogger(__name__)


class BaseSimpleAdminAuthorizationManagerException(Exception):
    """Base exception for :class:`SimpleAdminAuthorizationManager`."""


class NullablePasswordError(Exception):
    """Exception for situation when row is without password."""


class SimpleAdminAuthorizationManager(AdminSecretMixin):
    """Class for user registration.

    Manager does not provide real authorization. Each user could use preferred name.
    This name will be used for user authority. Each user is unique. Passwords not required.
    """

    def authorize_user(self, username: str, password: SecretStr) -> Optional[SystemUserModel]:
        user = self._system_user_storage.get_user_by_credits(login=username)
        if user is None:
            user = self._system_user_storage.create_user(login=username, password=password)
        if user.password is None:
            raise NullablePasswordError(f"User with id={user.id} has not got password!")
        if user.password.get_secret_value() == password.get_secret_value():
            return user
        return None
