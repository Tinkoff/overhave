from typing import cast

from pydantic.main import BaseModel

from overhave.publication.gitlab.tokenizer.settings import TokenizerClientSettings
from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import HttpMethod


class TokenizerResponse(BaseModel):
    """ Response from service tokenizer with token. """

    token: str


class TokenizerClient(BaseHttpClient[TokenizerClientSettings]):
    """ Client for sending requests for getting tokens for gitlab. """

    def __init__(self, settings: TokenizerClientSettings):
        super().__init__(settings)
        self._settings = settings

    def get_token(self, draft_id: int) -> TokenizerResponse:
        print(self._settings)
        response = self._make_request(
            HttpMethod.POST,
            self._settings.url,
            params={
                "initiator": self._settings.initiator,
                "id": draft_id,
                "vault_server_name": self._settings.vault_server_name,
            },
        )
        return cast(TokenizerResponse, self._parse_or_raise(response, TokenizerResponse))
