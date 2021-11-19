import logging
from typing import Optional

from pydantic import SecretStr

from overhave.authorization.manager.secret_mixin import AdminSecretMixin
from overhave.entities import SystemUserModel

logger = logging.getLogger(__name__)


class DefaultAdminAuthorizationManager(AdminSecretMixin):
    """Class for user authorization.

    Manager authorize users with registered credentials.
    """

    def authorize_user(self, username: str, password: SecretStr) -> Optional[SystemUserModel]:
        return self._system_user_storage.get_user_by_credits(login=username, password=password)
