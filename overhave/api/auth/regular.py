from http import HTTPStatus

import fastapi
from fastapi import security as fastapi_security
from jose import JWTError

from overhave.api.auth.models import AUTH_HEADERS
from overhave.api.auth.token import get_token_data
from overhave.api.deps import get_api_auth_settings, get_system_user_storage
from overhave.api.settings import OverhaveApiAuthSettings
from overhave.storage import ISystemUserStorage, SystemUserModel

oauth2_scheme = fastapi_security.OAuth2PasswordBearer(tokenUrl="token")


def get_authorized_user(
    token: str = fastapi.Depends(oauth2_scheme),
    auth_settings: OverhaveApiAuthSettings = fastapi.Depends(get_api_auth_settings),
    storage: ISystemUserStorage = fastapi.Depends(get_system_user_storage),
) -> SystemUserModel:
    creds_exception = fastapi.HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers=AUTH_HEADERS.dict(),
    )
    try:
        token_data = get_token_data(auth_settings=auth_settings, token=token)
        if token_data is None:
            raise creds_exception
    except JWTError:
        raise creds_exception
    user = storage.get_user_by_credits(login=token_data.username)
    if user is None:
        raise creds_exception
    return user
