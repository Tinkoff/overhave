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

    def _assign_admin_if_neccessary(self, session: so.Session, user_id: int, user_groups: list[str]) -> None:
        if self._settings.ldap_admin_group not in user_groups:
            return
        self._system_user_storage.update_user_role(session=session, user_id=user_id, role=db.Role.admin)

    def _is_user_can_be_created(self, session: so.Session, user_groups: list[str]) -> bool:
        return self._settings.ldap_admin_group in user_groups or self._system_user_group_storage.has_any_group(
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
            # TODO: в коде оперировать db.User, и уже в самом конце возвращать SystemUserModel
            user = self._system_user_storage.get_user_by_credits(session=session, login=username)
            if user is not None:
                self._assign_admin_if_neccessary(session=session, user_id=user.id, user_groups=user_groups)
                return user
            logger.debug("Have not found user with username '%s'!", username)
            if self._is_user_can_be_created(session=session, user_groups=user_groups):
                user = self._system_user_storage.create_user(session=session, login=username)
                self._assign_admin_if_neccessary(session=session, user_id=user.id, user_groups=user_groups)
                return user

        logger.debug("Received user groups (%s) are not supplied with database groups!", user_groups)
        return None
