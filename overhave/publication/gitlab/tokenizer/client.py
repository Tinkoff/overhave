from typing import Optional, cast

from pydantic.main import BaseModel

from overhave.publication.gitlab.tokenizer.settings import TokenizerClientSettings
from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import HttpMethod


class TokenizerResponse(BaseModel):
    """ Response from service tokenizer with token. """

    token: Optional[str]


class TokenizerClient(BaseHttpClient[TokenizerClientSettings]):
    """ Client for sending requests for getting tokens for gitlab. """

    def __init__(self, settings: TokenizerClientSettings):
        super().__init__(settings)
        self._settings = settings

    def get_token(self, initiator: str, draft_id: int) -> TokenizerResponse:
        if self._settings.vault_server_name is None:
            return TokenizerResponse(token=None)
        response = self._make_request(
            HttpMethod.POST,
            self._settings.url,
            params={"initiator": initiator, "id": draft_id, "vault_server_name": self._settings.vault_server_name},
        )
        return cast(TokenizerResponse, self._parse_or_raise(response, TokenizerResponse))
