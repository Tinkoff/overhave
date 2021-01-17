import abc
from typing import Optional

from wtforms import PasswordField, StringField

from overhave.db.users import BaseUser


class IAdminAuthorizationManager(abc.ABC):
    """ Abstract class for authorization manager. """

    @abc.abstractmethod
    def authorize_user(self, username_field: StringField, password_field: PasswordField) -> Optional[BaseUser]:
        pass
