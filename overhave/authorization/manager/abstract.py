import abc
from typing import Optional

from pydantic import SecretStr

from overhave.entities import SystemUserModel


class IAdminAuthorizationManager(abc.ABC):
    """Abstract class for authorization manager."""

    @abc.abstractmethod
    def authorize_user(self, username: str, password: SecretStr) -> Optional[SystemUserModel]:
        pass
