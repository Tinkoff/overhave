import os
import tempfile
from pathlib import Path
from typing import Callable
from uuid import uuid1

import pytest
from faker import Faker
from flask.testing import FlaskClient
from pytest_mock import MockFixture

from overhave import OverhaveAdminApp, OverhaveLdapManagerSettings, overhave_app
from overhave.admin.flask.login_manager import AdminPanelUser
from overhave.admin.views.index.login_form import LoginForm
from overhave.base_settings import DataBaseSettings
from overhave.entities import LDAPAdminAuthorizationManager
from overhave.factory import IAdminFactory
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.pytest_plugin import IProxyManager
from overhave.storage import SystemUserGroupStorage, SystemUserModel, SystemUserStorage
from overhave.transport import LDAPAuthenticator


@pytest.fixture()
def mocked_ldap_authenticator(mocker: MockFixture) -> LDAPAuthenticator:
    mocked = mocker.create_autospec(LDAPAuthenticator)
    mocked.get_user_groups.return_value = None
    return mocked


@pytest.fixture()
def test_ldap_manager_settings(faker) -> OverhaveLdapManagerSettings:
    return OverhaveLdapManagerSettings(ldap_admin_group=faker.word())


@pytest.fixture()
def test_ldap_auth_manager(
    test_system_user_storage: SystemUserStorage,
    test_system_user_group_storage: SystemUserGroupStorage,
    mocked_ldap_authenticator: LDAPAuthenticator,
    test_ldap_manager_settings: OverhaveLdapManagerSettings,
) -> LDAPAdminAuthorizationManager:
    return LDAPAdminAuthorizationManager(
        settings=test_ldap_manager_settings,
        system_user_storage=test_system_user_storage,
        system_user_group_storage=test_system_user_group_storage,
        ldap_authenticator=mocked_ldap_authenticator,
    )


@pytest.fixture()
def patched_app_admin_factory(
    db_settings: DataBaseSettings,
    database: None,
    mocked_context: BaseFactoryContext,
    clean_admin_factory: Callable[[], IAdminFactory],
    test_ldap_auth_manager,
) -> IAdminFactory:
    db_settings.setup_engine()
    factory = clean_admin_factory()
    factory.set_context(mocked_context)
    factory.auth_manager = test_ldap_auth_manager
    return factory


@pytest.fixture()
def test_pullrequest_id(faker: Faker) -> int:
    return faker.random_int()


@pytest.fixture()
def test_pullrequest_published_by() -> str:
    return uuid1().hex


@pytest.fixture()
def test_report_without_index(patched_app_admin_factory: IAdminFactory) -> Path:
    report_dir = patched_app_admin_factory.context.file_settings.tmp_reports_dir / uuid1().hex
    report_dir.mkdir()
    return report_dir


@pytest.fixture()
def test_report_with_index(test_report_without_index: Path, faker: Faker) -> Path:
    report_index = test_report_without_index / "index.html"
    report_index.write_text(faker.word())
    yield test_report_without_index
    report_index.unlink()


@pytest.fixture()
def test_app(
    clean_proxy_manager: Callable[[], IProxyManager], patched_app_admin_factory: IAdminFactory
) -> OverhaveAdminApp:
    return overhave_app(factory=patched_app_admin_factory)


@pytest.fixture()
def test_client(test_app: OverhaveAdminApp) -> FlaskClient:
    db_fd, test_app.config["DATABASE"] = tempfile.mkstemp()
    test_app.config["TESTING"] = True

    with test_app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(test_app.config["DATABASE"])


@pytest.fixture()
def test_authorized_user(test_client: FlaskClient, service_system_user: SystemUserModel) -> SystemUserModel:
    LoginForm.validate_on_submit = lambda self: True
    LoginForm.get_user = lambda self: AdminPanelUser(user_data=service_system_user)
    test_client.post("/login")
    return service_system_user
