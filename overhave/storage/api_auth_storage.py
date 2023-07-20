import abc
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from overhave.utils import get_current_time


class AuthToken(BaseModel):
    """Model for OAuth2 auth_managers token."""

    access_token: str
    expires_at: datetime
    token_type: Literal["Bearer"] = "Bearer"


class IAuthStorage(abc.ABC):
    """Abstract storage for auth_managers tokens."""

    @abc.abstractmethod
    def get_auth_token(self, username: str) -> AuthToken | None:
        pass

    @abc.abstractmethod
    def update_auth_token(self, username: str, new_auth_token: AuthToken) -> None:
        pass


class AuthStorage(IAuthStorage):
    """In-memory storage for auth_managers tokens."""

    def __init__(self) -> None:
        self._storage: dict[str, AuthToken] = {}

    def get_auth_token(self, username: str) -> AuthToken | None:
        auth_token = self._storage.get(username)
        if auth_token and auth_token.expires_at > get_current_time():
            return auth_token
        return None

    def update_auth_token(self, username: str, new_auth_token: AuthToken) -> None:
        self._storage[username] = new_auth_token
