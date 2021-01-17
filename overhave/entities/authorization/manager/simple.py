import logging
from typing import Optional, cast

from wtforms import PasswordField, StringField

from overhave import db
from overhave.entities.authorization.manager.secret_mixin import AdminSecretMixin

logger = logging.getLogger(__name__)


class SimpleAdminAuthorizationManager(AdminSecretMixin):
    """ Class for user registration via database.

    Manager does not provide real authorization. Every user could use preferred name.
    This name will be used for user authority. Every user is unique. Passwords not required.
    """

    def authorize_user(self, username_field: StringField, password_field: PasswordField) -> Optional[db.BaseUser]:
        with db.create_session(expire_on_commit=False) as s:
            db_user = s.query(db.UserRole).filter(db.UserRole.login == username_field.data).one_or_none()
            if db_user is None:
                db_user = self._create_user(session=s, username=username_field.data, password=password_field.data)
            if db_user.password == password_field.data:
                return cast(db.BaseUser, db_user)
            return None
