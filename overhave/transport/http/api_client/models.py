from typing import Literal

from pydantic import BaseModel


class TokenRequestData(BaseModel):
    """Model for OAuth2 request data."""

    grant_type: Literal["password"] = "password"
    username: str
    password: str
