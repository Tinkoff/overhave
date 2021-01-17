import abc
import logging
from uuid import UUID, uuid4

from overhave import db
from overhave.entities.authorization.manager.base import BaseAdminAuthorizationManager
from overhave.entities.authorization.settings import OverhaveAuthorizationSettings

logger = logging.getLogger(__name__)
_ADMIN_USERNAME = "admin"


class AdminSecretMixin(BaseAdminAuthorizationManager, abc.ABC):
    """
    Special class for default admin user preparation.

    Usage: application will create 'admin' user with UUID randomly generated secret key.
    This user will be placed into database, moreover key will be logged with INFO logging level.
    Note: real service administrator should bring this key and change password or delete this user!
    """

    def __init__(self, settings: OverhaveAuthorizationSettings):
        super().__init__(settings)
        self._make_secret()

    @staticmethod
    def _get_secret() -> UUID:
        return uuid4()

    @classmethod
    def _make_secret(cls) -> None:
        with db.create_session(expire_on_commit=False) as session:
            db_user = session.query(db.UserRole).filter(db.UserRole.login == _ADMIN_USERNAME).one_or_none()
            if db_user is not None:
                logger.info("Admin user already exists")
                return
            secret = cls._get_secret()
            logger.info("Generated admin secret: %s", secret)
            cls._create_user(session=session, username=_ADMIN_USERNAME, password=str(secret), role=db.Role.admin)
