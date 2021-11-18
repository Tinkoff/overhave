from typing import Dict, Union, cast

from pydantic.main import BaseModel

from overhave.publication.gitlab.tokenizer.settings import TokenizerClientSettings
from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import HttpMethod


class TokenizerResponse(BaseModel):
    """Response from service tokenizer with token."""

    token: str


class TokenizerRequestParamsModel(BaseModel):
    """Request for service tokenizer."""

    initiator: str
    id: int
    remote_key: str

    def get_request_params(self, remote_key_name: str) -> Dict[str, Union[int, str]]:
        return {"initiator": self.initiator, "id": self.id, remote_key_name: self.remote_key}


class BaseTokenizerException(Exception):
    """Base tokenizer exception."""


class InvalidUrlException(BaseTokenizerException):
    """Exception for case when tokenizer url is None."""


class InvalidRemoteKeyNameException(BaseTokenizerException):
    """Exception for case when tokenizer remote key name is None."""


class TokenizerClient(BaseHttpClient[TokenizerClientSettings]):
    """Client for sending requests for getting tokens for gitlab."""

    def __init__(self, settings: TokenizerClientSettings):
        super().__init__(settings)
        self._settings = settings

    def get_token(self, draft_id: int) -> TokenizerResponse:
        params_model = TokenizerRequestParamsModel(
            initiator=self._settings.initiator, id=draft_id, remote_key=self._settings.remote_key
        )
        if self._settings.url is None:
            raise InvalidUrlException("Please check tokenizer url! Value is invalid!")
        if self._settings.remote_key_name is None:
            raise InvalidRemoteKeyNameException("Please check remote key name! Value is invalid!")
        response = self._make_request(
            HttpMethod.POST,
            self._settings.url,
            params=params_model.get_request_params(self._settings.remote_key_name),
        )
        return cast(TokenizerResponse, self._parse_or_raise(response, TokenizerResponse))
