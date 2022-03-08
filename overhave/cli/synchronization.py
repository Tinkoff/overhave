import typer

from overhave.base_settings import DataBaseSettings, LoggingSettings
from overhave.cli.group import overhave
from overhave.factory import get_synchronizer_factory
from overhave.synchronization import IOverhaveSynchronizer


def _create_synchronizer() -> IOverhaveSynchronizer:
    DataBaseSettings().setup_db()
    LoggingSettings().setup_logging()
    return get_synchronizer_factory().synchronizer


@overhave.command(short_help="Run Overhave feature synchronization")
def synchronize(
    create_db_features: bool = typer.Option(
        False, "-c", "--create-db-features", is_flag=True, help="Create features in database if necessary"
    ),
    pull_repository: bool = typer.Option(False, "-p", "--pull-repository", is_flag=True, help="Pull remote repository"),
) -> None:
    _create_synchronizer().synchronize(create_db_features, pull_repository)
