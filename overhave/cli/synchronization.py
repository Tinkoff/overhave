import click

from overhave.base_settings import DataBaseSettings, LoggingSettings
from overhave.cli.group import overhave
from overhave.factory import get_synchronizer_factory
from overhave.synchronization import IOverhaveSynchronizer


def _create_synchronizer() -> IOverhaveSynchronizer:
    DataBaseSettings().setup_db()
    LoggingSettings().setup_logging()
    return get_synchronizer_factory().synchronizer


@overhave.command(short_help="Run Overhave feature synchronization")
@click.option("-c", "--create-db-features", is_flag=True, help="Create features in database if necessary")
def synchronize(create_db_features: bool) -> None:
    _create_synchronizer().synchronize(create_db_features)
