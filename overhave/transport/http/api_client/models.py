from pydantic.fields import Field
from pydantic.main import BaseModel


class TokenRequestData(BaseModel):
    """Model for OAuth2 request data."""

    grant_type: str = Field("password", const=True)
    username: str
    password: str
