import pytest

from overhave.storage import SystemUserGroupStorage, SystemUserStorage


@pytest.fixture(scope="package")
def test_system_user_storage() -> SystemUserStorage:
    return SystemUserStorage()


@pytest.fixture(scope="package")
def test_system_user_group_storage() -> SystemUserGroupStorage:
    return SystemUserGroupStorage()
