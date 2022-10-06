from functools import cache
from pathlib import Path

from overhave.api.settings import OverhaveApiAuthSettings
from overhave.entities import OverhaveEmulationSettings, OverhaveRedisSettings
from overhave.storage import (
    DraftStorage,
    EmulationStorage,
    FeatureStorage,
    FeatureTagStorage,
    FeatureTypeStorage,
    IDraftStorage,
    IEmulationStorage,
    IFeatureStorage,
    IFeatureTagStorage,
    IFeatureTypeStorage,
    IScenarioStorage,
    ISystemUserStorage,
    ITestRunStorage,
    ITestUserStorage,
    ScenarioStorage,
    SystemUserStorage,
    TestRunStorage,
    TestUserStorage,
)
from overhave.transport import EmulationTask, PublicationTask, RedisProducer, RedisStream, TestRunTask


@cache
def get_api_auth_settings() -> OverhaveApiAuthSettings:
    return OverhaveApiAuthSettings()


@cache
def get_admin_files_dir() -> Path:
    return Path(__file__).parent.parent / "admin" / "files"


@cache
def get_system_user_storage() -> ISystemUserStorage:
    return SystemUserStorage()


@cache
def get_feature_tag_storage() -> IFeatureTagStorage:
    return FeatureTagStorage()


@cache
def get_scenario_storage() -> IScenarioStorage:
    return ScenarioStorage()


@cache
def get_feature_type_storage() -> IFeatureTypeStorage:
    return FeatureTypeStorage()


@cache
def get_feature_storage() -> IFeatureStorage:
    return FeatureStorage()


@cache
def get_draft_storage() -> IDraftStorage:
    return DraftStorage()


@cache
def get_test_user_storage() -> ITestUserStorage:
    return TestUserStorage()


@cache
def get_test_run_storage() -> ITestRunStorage:
    return TestRunStorage()


@cache
def get_emulation_storage() -> IEmulationStorage:
    return EmulationStorage(OverhaveEmulationSettings())


@cache
def get_redis_producer() -> RedisProducer:
    return RedisProducer(
        settings=OverhaveRedisSettings(),
        mapping={
            TestRunTask: RedisStream.TEST,
            PublicationTask: RedisStream.PUBLICATION,
            EmulationTask: RedisStream.EMULATION,
        },
    )
