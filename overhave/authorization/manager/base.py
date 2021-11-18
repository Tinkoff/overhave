import abc
import logging

from overhave.authorization.manager.abstract import IAdminAuthorizationManager
from overhave.authorization.settings import OverhaveAuthorizationSettings
from overhave.storage import ISystemUserStorage

logger = logging.getLogger(__name__)


class BaseAdminAuthorizationManager(IAdminAuthorizationManager, abc.ABC):
    """Base class for user authorization."""

    def __init__(self, settings: OverhaveAuthorizationSettings, system_user_storage: ISystemUserStorage):
        self._settings = settings
        self._system_user_storage = system_user_storage
        logger.info("Authorization manager: %s", type(self))
