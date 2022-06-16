from http import HTTPStatus

import fastapi
from fastapi import security as fastapi_security
from pydantic.types import SecretStr

from overhave.api.auth import AUTH_HEADERS, create_access_token
from overhave.api.deps import get_api_auth_settings, get_system_user_storage
from overhave.api.settings import OverhaveApiAuthSettings
from overhave.storage import AuthToken, ISystemUserStorage
from overhave.utils import get_current_time


def login_for_access_token(
    form_data: fastapi_security.OAuth2PasswordRequestForm = fastapi.Depends(),
    auth_settings: OverhaveApiAuthSettings = fastapi.Depends(get_api_auth_settings),
    storage: ISystemUserStorage = fastapi.Depends(get_system_user_storage),
) -> AuthToken:
    user = storage.get_user_by_credits(login=form_data.username, password=SecretStr(form_data.password))
    if not user:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers=AUTH_HEADERS.dict(),
        )
    expires_at = get_current_time() + auth_settings.access_token_expire_timedelta
    access_token = create_access_token(auth_settings=auth_settings, username=form_data.username, expires_at=expires_at)
    return AuthToken(access_token=access_token, expires_at=expires_at)
