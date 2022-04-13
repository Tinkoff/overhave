from functools import cache
from pathlib import Path

from overhave.api.settings import OverhaveApiAuthSettings
from overhave.storage import (
    FeatureTagStorage,
    IFeatureTagStorage,
    ISystemUserStorage,
    ITestUserStorage,
    SystemUserStorage,
    TestUserStorage,
)


@cache
def get_test_user_storage() -> ITestUserStorage:
    return TestUserStorage()


@cache
def get_feature_tag_storage() -> IFeatureTagStorage:
    return FeatureTagStorage()


@cache
def get_system_user_storage() -> ISystemUserStorage:
    return SystemUserStorage()


@cache
def get_api_auth_settings() -> OverhaveApiAuthSettings:
    return OverhaveApiAuthSettings()


@cache
def get_admin_files_dir() -> Path:
    return Path(__file__).parent.parent / "admin" / "files"
