from typing import Callable

import pytest

from demo.demo import _prepare_synchronizer_factory
from demo.settings import OverhaveDemoSettingsGenerator
from overhave import overhave_synchronizer_factory
from overhave.cli.synchronization import _create_synchronizer
from overhave.factory import ISynchronizerFactory
from overhave.synchronization import OverhaveSynchronizer


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
    mock_envs: None,
    database: None,
    test_demo_settings_generator: OverhaveDemoSettingsGenerator,
) -> OverhaveSynchronizer:
    _prepare_synchronizer_factory(settings_generator=test_demo_settings_generator)
    return _create_synchronizer()
