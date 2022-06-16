import logging
from typing import Optional

from pydantic.types import SecretStr

from overhave.storage import AuthStorage, AuthToken
from overhave.transport.http.api_client.models import TokenRequestData
from overhave.transport.http.api_client.settings import OverhaveApiAuthenticatorSettings
from overhave.transport.http.base_client import BaseHttpClient, BearerAuth, HttpMethod

logger = logging.getLogger(__name__)


class OverhaveApiAuthenticator(BaseHttpClient[OverhaveApiAuthenticatorSettings]):
    """Client for auth_managers in Overhave API."""

    def __init__(
        self,
        settings: OverhaveApiAuthenticatorSettings,
        auth_storage: AuthStorage,
    ):
        super().__init__(settings=settings)
        self._auth_storage = auth_storage

    def _auth_by_credentials(self, username: str, password: SecretStr) -> AuthToken:
        logger.info("Get auth_managers token by username and password")
        data = TokenRequestData(username=username, password=password.get_secret_value())
        response = self._make_request(
            method=HttpMethod.POST,
            url=self._settings.get_auth_token_url,
            data=data.dict(by_alias=True),
        )
        return AuthToken.parse_obj(response.json())

    def _get_auth_token(self, username: str, password: SecretStr) -> AuthToken:
        token: Optional[AuthToken] = self._auth_storage.get_auth_token(username=username)
        if token is None:
            token = self._auth_by_credentials(username=username, password=password)
            self._auth_storage.update_auth_token(username=username, new_auth_token=token)
        return token

    def get_bearer_auth(self, username: str, password: SecretStr) -> BearerAuth:
        token = self._get_auth_token(username=username, password=password)
        return BearerAuth(token.access_token)
