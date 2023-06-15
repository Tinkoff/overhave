import abc

from pydantic import SecretStr

from overhave.storage import SystemUserModel


class IAdminAuthorizationManager(abc.ABC):
    """Abstract class for auth_managers manager."""

    @abc.abstractmethod
    def authorize_user(self, username: str, password: SecretStr) -> SystemUserModel | None:
        pass
