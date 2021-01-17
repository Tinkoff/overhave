import abc
import logging
from typing import Optional

import sqlalchemy.orm as so

from overhave import db
from overhave.entities.authorization.manager.abstract import IAdminAuthorizationManager
from overhave.entities.authorization.settings import OverhaveAuthorizationSettings

logger = logging.getLogger(__name__)


class BaseAdminAuthorizationManager(IAdminAuthorizationManager, abc.ABC):
    """ Base class for user authorization. """

    def __init__(self, settings: OverhaveAuthorizationSettings):
        self._settings = settings
        logger.info("Authorization manager: %s", type(self))

    @staticmethod
    def _create_user(
        session: so.Session, username: str, password: Optional[str] = None, role: db.Role = db.Role.user
    ) -> db.UserRole:
        db_user = db.UserRole(login=username, password=password, role=role)
        session.add(db_user)
        session.commit()
        return db_user
