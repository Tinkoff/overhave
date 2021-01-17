import logging
from pprint import pformat
from typing import List, Optional, cast

import sqlalchemy.orm as so
from wtforms import PasswordField, StringField

from overhave import db
from overhave.entities.authorization.manager.base import BaseAdminAuthorizationManager
from overhave.entities.authorization.manager.ldap.authenticator import LDAPAuthenticator
from overhave.entities.authorization.settings import OverhaveAuthorizationSettings

logger = logging.getLogger(__name__)


class LDAPEmptyAdminGroupError(ValueError):
    """ Exception for situation with empty LDAP admin group. """

    pass


class LDAPAdminAuthorizationManager(BaseAdminAuthorizationManager):
    """ Class for user authorization via LDAP.

    Manager authorize users using remote LDAP server. Every user should use his LDAP credentials.
    LDAP server returns user groups. If user in default 'admin' group or his groups list contains admin group - user
    will be authorized. If user already placed in database - user will be authorized too. No one password stores.
    """

    def __init__(self, settings: OverhaveAuthorizationSettings, ldap_authenticator: LDAPAuthenticator):
        if settings.admin_group is None:
            raise LDAPEmptyAdminGroupError("Admin group could not be empty!")
        super().__init__(settings)
        self._ldap_authenticator = ldap_authenticator

    def _reassign_role_if_neccessary(self, session: so.Session, user: db.UserRole, user_groups: List[str]) -> None:
        if self._settings.admin_group is not None and self._settings.admin_group in user_groups:
            user.role = db.Role.admin
            session.add(user)
            session.commit()

    def authorize_user(self, username_field: StringField, password_field: PasswordField) -> Optional[db.BaseUser]:
        logger.debug("Try to authorize user '%s'...", username_field.data)
        user_groups = self._ldap_authenticator.get_user_groups(username_field.data, password_field.data)
        if not user_groups:
            logger.debug('LDAP user does not exist!')
            return None
        logger.debug('LDAP user groups: \n %s', pformat(user_groups))
        with db.create_session(expire_on_commit=False) as s:
            db_user = s.query(db.UserRole).filter(db.UserRole.login == username_field.data).one_or_none()
            if db_user is not None:
                self._reassign_role_if_neccessary(session=s, user=db_user, user_groups=user_groups)
                return cast(db.BaseUser, db_user)
            logger.debug("Have not found user with username '%s'!", username_field.data)
            db_groups = s.query(db.GroupRole).filter(db.GroupRole.group.in_(user_groups)).all()
            if db_groups or self._settings.admin_group in user_groups:
                db_user = self._create_user(session=s, username=username_field.data)
                self._reassign_role_if_neccessary(session=s, user=db_user, user_groups=user_groups)
                return cast(db.BaseUser, db_user)
            logger.debug('Received groups are not supplied with db_groups: \n %s', db_groups)
        return None
