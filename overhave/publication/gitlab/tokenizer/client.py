from typing import cast

from pydantic.fields import Field
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
    remote_key = Field(str, alias="vault_server_name")


class TokenizerClient(BaseHttpClient[TokenizerClientSettings]):
    """ Client for sending requests for getting tokens for gitlab. """

    def __init__(self, settings: TokenizerClientSettings):
        super().__init__(settings)
        self._settings = settings

    def get_token(self, draft_id: int) -> TokenizerResponse:
        response = self._make_request(
            HttpMethod.POST,
            self._settings.url,  # type: ignore
            params=TokenizerRequestParamsModel(
                initiator=self._settings.initiator, id=draft_id, remote_key=self._settings.remote_key
            ).dict(by_alias=True),
        )
        return cast(TokenizerResponse, self._parse_or_raise(response, TokenizerResponse))
