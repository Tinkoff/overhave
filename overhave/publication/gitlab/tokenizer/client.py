from typing import cast

from pydantic.main import BaseModel

from overhave.publication.gitlab.tokenizer.settings import TokenizerClientSettings
from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import HttpMethod


class TokenizerResponse(BaseModel):
    """ Response from service tokenizer with token. """

    token: str


class TokenizerRequestParamsModel(BaseModel):
    """ Request for service tokenizer. """

    initiator: str
    id: int
    remote_key: str


class TokenizerClient(BaseHttpClient[TokenizerClientSettings]):
    """ Client for sending requests for getting tokens for gitlab. """

    def __init__(self, settings: TokenizerClientSettings):
        super().__init__(settings)
        self._settings = settings

    def get_token(self, draft_id: int) -> TokenizerResponse:
        params = TokenizerRequestParamsModel(
            initiator=self._settings.initiator, id=draft_id, remote_key=self._settings.remote_key
        ).dict()
        if self._settings.remote_key_name != "remote_key":
            params[self._settings.remote_key_name] = params["remote_key"]  # type: ignore
            params.pop("remote_key")
        response = self._make_request(
            HttpMethod.POST,
            self._settings.url,  # type: ignore
            params=params,
        )
        return cast(TokenizerResponse, self._parse_or_raise(response, TokenizerResponse))
