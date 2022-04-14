import abc
import logging

from overhave.entities.auth_managers.abstract import IAdminAuthorizationManager
from overhave.storage import ISystemUserStorage

logger = logging.getLogger(__name__)


class BaseAdminAuthorizationManager(IAdminAuthorizationManager, abc.ABC):
    """Base class for user auth_managers."""

    def __init__(self, system_user_storage: ISystemUserStorage):
        self._system_user_storage = system_user_storage
        logger.info("Authorization manager: %s", type(self))
