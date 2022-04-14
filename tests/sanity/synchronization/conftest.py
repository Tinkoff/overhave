from typing import Callable, List
from unittest import mock

import pytest

from demo.demo import _prepare_synchronizer_factory
from demo.settings import OverhaveDemoSettingsGenerator
from overhave import db, overhave_synchronizer_factory
from overhave.cli.synchronization import _create_synchronizer
from overhave.factory import ISynchronizerFactory
from overhave.storage import FeatureTypeModel
from overhave.synchronization import IOverhaveSynchronizer
from tests.objects import get_test_feature_containers


@pytest.fixture()
def clean_synchronizer_factory() -> Callable[[], ISynchronizerFactory]:
    overhave_synchronizer_factory.cache_clear()
    return overhave_synchronizer_factory


@pytest.fixture()
def test_synchronizer_factory(clean_synchronizer_factory: Callable[[], ISynchronizerFactory]) -> ISynchronizerFactory:
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
def test_db_feature_types(database: None) -> List[FeatureTypeModel]:
    feature_types = [feature.type for feature in get_test_feature_containers()]
    with db.create_session() as session:
        session.add_all((db.FeatureType(name=feature_type) for feature_type in feature_types))
        session.flush()
        db_feature_types = session.query(db.FeatureType).all()
        return [FeatureTypeModel.from_orm(db_feature_type) for db_feature_type in db_feature_types]
