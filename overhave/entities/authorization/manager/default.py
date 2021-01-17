import logging
from typing import Optional, cast

from wtforms import PasswordField, StringField

from overhave import db
from overhave.entities.authorization.manager.secret_mixin import AdminSecretMixin

logger = logging.getLogger(__name__)


class DefaultAdminAuthorizationManager(AdminSecretMixin):
    """ Class for user authorization via database.

    Manager authorize users with registered credentials from database.
    """

    def authorize_user(self, username_field: StringField, password_field: PasswordField) -> Optional[db.BaseUser]:
        with db.create_session(expire_on_commit=False) as s:
            db_user = (
                s.query(db.UserRole)
                .filter(db.UserRole.login == username_field.data, db.UserRole.password == password_field.data)
                .one_or_none()
            )
            if db_user is not None:
                return cast(db.BaseUser, db_user)
        return None
