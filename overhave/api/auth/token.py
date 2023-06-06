from datetime import datetime
from typing import cast

from jose import jwt

from overhave.api.auth.models import AuthTokenData
from overhave.api.settings import OverhaveApiAuthSettings


def create_access_token(auth_settings: OverhaveApiAuthSettings, username: str, expires_at: datetime) -> str:
    to_encode: dict[str, str | datetime] = {"sub": username, "exp": expires_at}
    return cast(
        str, jwt.encode(to_encode, auth_settings.secret_key.get_secret_value(), algorithm=auth_settings.algorithm)
    )


def get_token_data(auth_settings: OverhaveApiAuthSettings, token: str) -> AuthTokenData | None:
    payload = jwt.decode(token, auth_settings.secret_key.get_secret_value(), algorithms=[auth_settings.algorithm])
    username: str | None = payload.get("sub")
    if username is not None:
        return AuthTokenData(username=username)
    return None
