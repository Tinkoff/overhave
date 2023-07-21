import logging
from pprint import pformat

import sqlalchemy.orm as so
from pydantic import SecretStr

from overhave import db
from overhave.entities.auth_managers.base import BaseAdminAuthorizationManager
from overhave.entities.auth_managers.ldap.settings import OverhaveLdapManagerSettings
from overhave.storage import ISystemUserGroupStorage, ISystemUserStorage, SystemUserModel
from overhave.transport.ldap.authenticator import LDAPAuthenticator

logger = logging.getLogger(__name__)


class LDAPEmptyAdminGroupError(ValueError):
    """Exception for situation with empty LDAP admin group."""


class LDAPAdminAuthorizationManager(BaseAdminAuthorizationManager):
    """Class for user auth_managers via LDAP.

    Manager authorize users using remote LDAP server. Each user should use his LDAP credentials.
    LDAP server returns user groups. If user in default 'admin' group or his groups list contains admin group - user
    will be authorized. If user already placed in database - user will be authorized too. No one password stores.
    """

    def __init__(
        self,
        settings: OverhaveLdapManagerSettings,
        system_user_storage: ISystemUserStorage,
        system_user_group_storage: ISystemUserGroupStorage,
        ldap_authenticator: LDAPAuthenticator,
    ):
        super().__init__(system_user_storage)
        self._settings = settings
        self._system_user_group_storage = system_user_group_storage
        self._ldap_authenticator = ldap_authenticator

    @staticmethod
    def _user_role_by_admin_group_entry(user_has_admin_group: bool) -> db.Role:
        if user_has_admin_group:
            return db.Role.admin
        return db.Role.user

    def _can_user_be_created(self, session: so.Session, user_has_admin_group: bool, user_groups: list[str]) -> bool:
        return user_has_admin_group or self._system_user_group_storage.has_any_group(
            session=session, user_groups=user_groups
        )

    def authorize_user(self, username: str, password: SecretStr) -> SystemUserModel | None:
        logger.debug("Try to authorize user '%s'...", username)
        user_groups = self._ldap_authenticator.get_user_groups(username, password)
        if not user_groups:
            logger.info("LDAP user '%s' does not exist!", username)
            return None
        logger.debug("LDAP user groups: \n %s", pformat(user_groups))

        with db.create_session() as session:
            user_has_admin_group = self._settings.ldap_admin_group in user_groups
            intended_user_role = self._user_role_by_admin_group_entry(user_has_admin_group)

            user = self._system_user_storage.get_user_by_credits(session=session, login=username)
            if user is not None:
                if user.role is db.Role.user and user.role is not intended_user_role:
                    user.role = intended_user_role
                    session.flush()
                return SystemUserModel.model_validate(user)

            logger.debug("Have not found user with username '%s'!", username)
            if self._can_user_be_created(
                session=session, user_has_admin_group=user_has_admin_group, user_groups=user_groups
            ):
                user = self._system_user_storage.create_user(session=session, login=username, role=intended_user_role)
                return SystemUserModel.model_validate(user)

        logger.debug("Received user groups (%s) are not supplied with exist groups!", user_groups)
        return None
