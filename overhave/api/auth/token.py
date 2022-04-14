from datetime import datetime
from typing import Dict, Optional, Union, cast

from jose import jwt

from overhave.api.auth.models import AuthTokenData
from overhave.api.settings import OverhaveApiAuthSettings


def create_access_token(auth_settings: OverhaveApiAuthSettings, username: str, expires_at: datetime) -> str:
    to_encode: Dict[str, Union[str, datetime]] = {"sub": username, "exp": expires_at}
    return cast(
        str, jwt.encode(to_encode, auth_settings.secret_key.get_secret_value(), algorithm=auth_settings.algorithm)
    )


def get_token_data(auth_settings: OverhaveApiAuthSettings, token: str) -> Optional[AuthTokenData]:
    payload = jwt.decode(token, auth_settings.secret_key.get_secret_value(), algorithms=[auth_settings.algorithm])
    username: Optional[str] = payload.get("sub")
    if username is not None:
        return AuthTokenData(username=username)
    return None
