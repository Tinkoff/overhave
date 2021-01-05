from functools import lru_cache
from pathlib import Path
from typing import Iterator

import pytest
import sqlalchemy_utils as sau
from sqlalchemy import MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import close_all_sessions
from sqlalchemy_utils import drop_database

from overhave import OverhaveFileSettings
from overhave.base_settings import DataBaseSettings, OverhaveLoggingSettings
from overhave.entities import FeatureExtractor
from tests.objects import DataBaseContext, XDistWorkerValueType


@lru_cache(maxsize=None)
def get_file_settings() -> OverhaveFileSettings:
    test_features_dir = Path(__file__).parent / 'test_features'
    return OverhaveFileSettings(
        fixtures_base_dir=test_features_dir, features_base_dir=test_features_dir, tmp_dir=test_features_dir / 'tmp'
    )


@lru_cache(maxsize=None)
def get_feature_extractor() -> FeatureExtractor:
    return FeatureExtractor(file_settings=get_file_settings())


@pytest.fixture(scope="session", autouse=True)
def setup_logging() -> None:
    OverhaveLoggingSettings().setup_logging()


@pytest.fixture(scope="session")
def db_settings(worker_id: XDistWorkerValueType) -> DataBaseSettings:
    settings = DataBaseSettings()
    settings.db_url = f"{settings.db_url}/overhave_{worker_id}"
    return settings


def create_metadata(db_context: DataBaseContext) -> None:
    db_context.metadata.bind = db_context.engine
    db_context.metadata.drop_all()
    db_context.metadata.create_all()


@pytest.fixture(scope='session')
def db_context(db_settings: DataBaseSettings) -> Iterator[DataBaseContext]:
    from overhave.db import metadata

    if sau.database_exists(db_settings.db_url):
        sau.drop_database(db_settings.db_url)
    sau.create_database(db_settings.db_url)
    engine = create_engine(db_settings.db_url, echo=db_settings.db_echo, pool_pre_ping=True)
    db_context = DataBaseContext(metadata=metadata, engine=engine)
    create_metadata(db_context)
    yield db_context
    drop_database(db_settings.db_url)


def truncate_all_tables(metadata: MetaData) -> None:
    connection = metadata.bind.connect()
    transaction = connection.begin()

    for table in metadata.sorted_tables:
        connection.execute(table.delete())

    transaction.commit()
    connection.close()


@pytest.fixture()
def database(db_context: DataBaseContext) -> Iterator[None]:
    truncate_all_tables(db_context.metadata)
    yield
    close_all_sessions()
