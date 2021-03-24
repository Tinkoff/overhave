from typing import Callable, Dict, Optional

import pytest

from overhave import OverhaveDBSettings, db
from overhave.entities import ScenarioModel, SystemUserModel
from overhave.pytest_plugin import IProxyManager
from tests.objects import PROJECT_WORKDIR, FeatureTestContainer


@pytest.fixture(scope="module")
def envs_for_mock(db_settings: OverhaveDBSettings) -> Dict[str, Optional[str]]:
    return {"OVERHAVE_DB_URL": str(db_settings.db_url), "OVERHAVE_WORK_DIR": PROJECT_WORKDIR.as_posix()}


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def test_proxy_manager(clean_proxy_manager: Callable[[], IProxyManager]) -> IProxyManager:
    return clean_proxy_manager()


@pytest.fixture()
def test_db_user(database: None) -> SystemUserModel:
    with db.create_session() as session:
        db_user = db.UserRole(login="test_user", password="test_password", role=db.Role.user)
        session.add(db_user)
        session.flush()
        return SystemUserModel.from_orm(db_user)


@pytest.fixture()
def test_db_scenario(test_feature_container: FeatureTestContainer, test_db_user: SystemUserModel) -> ScenarioModel:
    with db.create_session() as session:
        db_feature_type = session.query(db.FeatureType).filter(db.FeatureType.name == test_feature_container.type).one()
        db_feature = db.Feature(
            name=test_feature_container.name,
            author=test_db_user.login,
            type_id=db_feature_type.id,
            task=["PRJ-123"],
            last_edited_by=test_db_user.login,
        )
        session.add(db_feature)
        session.flush()
        db_scenario = db.Scenario(feature_id=db_feature.id, text=test_feature_container.scenario)
        session.add(db_scenario)
        session.flush()
        return ScenarioModel.from_orm(db_scenario)
