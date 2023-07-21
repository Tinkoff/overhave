import logging

from pydantic import SecretStr

from overhave import db
from overhave.entities.auth_managers.secret_mixin import AdminSecretMixin
from overhave.storage import SystemUserModel

logger = logging.getLogger(__name__)


class DefaultAdminAuthorizationManager(AdminSecretMixin):
    """Class for user auth_managers.

    Manager authorize users with registered credentials.
    """

    def authorize_user(self, username: str, password: SecretStr) -> SystemUserModel | None:
        with db.create_session() as session:
            user = self._system_user_storage.get_user_by_credits(session=session, login=username, password=password)
            if user is None:
                return None
            return SystemUserModel.model_validate(user)
