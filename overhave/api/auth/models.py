from pydantic.fields import Field
from pydantic.main import BaseModel


class AuthTokenData(BaseModel):
    """Model for OAuth2 auth_managers token data."""

    username: str


class AuthHeaders(BaseModel):
    """Model for OAuth2 auth_managers HTTP headers."""

    Authorization: str = Field("Bearer", const=True)


AUTH_HEADERS = AuthHeaders()
