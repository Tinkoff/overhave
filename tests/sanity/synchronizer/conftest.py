from typing import Callable
from unittest import mock

import pytest

from demo.demo import _prepare_synchronizer_factory
from demo.settings import OverhaveDemoSettingsGenerator
from overhave import db, overhave_synchronizer_factory
from overhave.cli.synchronizer import _create_synchronizer, _create_validator
from overhave.factory import ISynchronizerFactory
from overhave.scenario import FeatureValidator
from overhave.storage import FeatureTypeModel, SystemUserModel
from overhave.synchronization import IOverhaveSynchronizer
from tests.db_utils import create_test_session
from tests.objects import get_test_feature_containers


@pytest.fixture()
def clean_synchronizer_factory() -> Callable[[], ISynchronizerFactory]:
    overhave_synchronizer_factory.cache_clear()
    return overhave_synchronizer_factory


@pytest.fixture()
def prepared_admin_user(database: None) -> SystemUserModel:
    with create_test_session() as session:
        db_user = db.UserRole(login="admin", password="admin", role=db.Role.admin)
        session.add(db_user)
        session.flush()
        return SystemUserModel.from_orm(db_user)


@pytest.fixture()
def test_synchronizer_factory(
    clean_synchronizer_factory: Callable[[], ISynchronizerFactory], prepared_admin_user: SystemUserModel
) -> ISynchronizerFactory:
    return clean_synchronizer_factory()


@pytest.fixture()
def test_resolved_synchronizer(
    test_synchronizer_factory: ISynchronizerFactory,
    mocked_git_repo: mock.MagicMock,
    mock_envs: None,
    database: None,
    test_demo_settings_generator: OverhaveDemoSettingsGenerator,
) -> IOverhaveSynchronizer:
    _prepare_synchronizer_factory(settings_generator=test_demo_settings_generator)
    return _create_synchronizer()


@pytest.fixture()
def test_resolved_validator(
    test_synchronizer_factory: ISynchronizerFactory,
    mocked_git_repo: mock.MagicMock,
    mock_envs: None,
    test_demo_settings_generator: OverhaveDemoSettingsGenerator,
) -> FeatureValidator:
    _prepare_synchronizer_factory(settings_generator=test_demo_settings_generator)
    return _create_validator()


@pytest.fixture()
def test_db_feature_types(database: None) -> list[FeatureTypeModel]:
    feature_types = [feature.type for feature in get_test_feature_containers()]
    with create_test_session() as session:
        session.add_all((db.FeatureType(name=feature_type) for feature_type in feature_types))
        session.flush()
        db_feature_types = session.query(db.FeatureType).all()
        return [FeatureTypeModel.from_orm(db_feature_type) for db_feature_type in db_feature_types]
