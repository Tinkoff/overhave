import abc
import logging
from uuid import uuid4

from pydantic import SecretStr

from overhave import db
from overhave.authorization.manager.base import BaseAdminAuthorizationManager
from overhave.authorization.settings import OverhaveAuthorizationSettings
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

    def __init__(self, settings: OverhaveAuthorizationSettings, system_user_storage: ISystemUserStorage):
        super().__init__(settings, system_user_storage)
        self._make_secret()

    @staticmethod
    def _get_secret() -> SecretStr:
        return SecretStr(uuid4().hex)

    def _make_secret(self) -> None:
        user = self._system_user_storage.get_user_by_credits(login=_ADMIN_USERNAME)
        if user is not None:
            logger.info("Admin user already exists")
            return
        secret = self._get_secret()
        logger.info("Generated admin secret: %s", secret.get_secret_value())
        self._system_user_storage.create_user(login=_ADMIN_USERNAME, password=secret, role=db.Role.admin)
