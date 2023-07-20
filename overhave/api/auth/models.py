from typing import Literal

from pydantic.main import BaseModel


class AuthTokenData(BaseModel):
    """Model for OAuth2 auth_managers token data."""

    username: str


class AuthHeaders(BaseModel):
    """Model for OAuth2 auth_managers HTTP headers."""

    Authorization: Literal["Bearer"] = "Bearer"


AUTH_HEADERS: AuthHeaders = AuthHeaders()
