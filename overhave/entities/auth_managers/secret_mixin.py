import abc
import logging
from uuid import uuid4

from pydantic import SecretStr

from overhave import db
from overhave.entities.auth_managers.base import BaseAdminAuthorizationManager
from overhave.storage import ISystemUserStorage

logger = logging.getLogger(__name__)
_ADMIN_USERNAME = "admin"


class AdminSecretMixin(BaseAdminAuthorizationManager, abc.ABC):
    """
    Special class for default admin user preparation.

    Usage: application will create 'admin' user with UUID randomly generated secret key.
    This user will be placed into database, moreover key will be logged with INFO logging level.
    Note: real service administrator should bring this key and change password or delete this user!
    """

    def __init__(self, system_user_storage: ISystemUserStorage):
        super().__init__(system_user_storage)
        self._make_secret()

    @staticmethod
    def _get_secret() -> SecretStr:
        return SecretStr(uuid4().hex)

    def _make_secret(self) -> None:
        secret = self._get_secret()
        with db.create_session() as session:
            if self._system_user_storage.get_user_by_credits(session=session, login=_ADMIN_USERNAME):
                logger.info("Admin user already exists")
                return
            self._system_user_storage.create_user(
                session=session, login=_ADMIN_USERNAME, password=secret, role=db.Role.admin
            )
        logger.info("Generated admin secret: %s", secret.get_secret_value())
