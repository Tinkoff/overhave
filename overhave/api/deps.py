from functools import cache
from pathlib import Path

import walrus

from overhave.api.settings import OverhaveApiAuthSettings
from overhave.entities import OverhaveEmulationSettings
from overhave.metrics import get_common_metric_container
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
from overhave.transport.redis.deps import get_redis_settings, make_redis


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
def get_redis_database() -> walrus.Database:
    redis = make_redis(get_redis_settings())
    return walrus.Database(connection_pool=redis.connection_pool)


@cache
def get_redis_producer() -> RedisProducer:
    return RedisProducer(
        settings=get_redis_settings(),
        mapping={
            TestRunTask: RedisStream.TEST,
            PublicationTask: RedisStream.PUBLICATION,
            EmulationTask: RedisStream.EMULATION,
        },
        database=get_redis_database(),
        metric_container=get_common_metric_container(),
    )
