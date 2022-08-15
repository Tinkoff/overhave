import typer

from overhave.base_settings import DataBaseSettings, LoggingSettings
from overhave.factory import get_synchronizer_factory
from overhave.scenario import FeatureValidator
from overhave.synchronization import IOverhaveSynchronizer

sync_app = typer.Typer(short_help="Run Overhave features synchronization commands")


def _create_synchronizer() -> IOverhaveSynchronizer:
    DataBaseSettings().setup_db()
    LoggingSettings().setup_logging()
    return get_synchronizer_factory().synchronizer


@sync_app.command(short_help="Run Overhave features synchronization")
def run(
    create_db_features: bool = typer.Option(
        False, "-c", "--create-db-features", is_flag=True, help="Create features in database if necessary"
    ),
    pull_repository: bool = typer.Option(False, "-p", "--pull-repository", is_flag=True, help="Pull remote repository"),
) -> None:
    _create_synchronizer().synchronize(create_db_features, pull_repository)


def _create_validator() -> FeatureValidator:
    LoggingSettings().setup_logging()
    return get_synchronizer_factory().feature_validator


@sync_app.command(short_help="Run Overhave feature files validation")
def validate_features(
    raise_if_nullable_id: bool = typer.Option(
        False, "-r", "--raise-if-nullable-id", is_flag=True, help="Raise if validator find features with nullable IDs"
    ),
    pull_repository: bool = typer.Option(False, "-p", "--pull-repository", is_flag=True, help="Pull remote repository"),
) -> None:
    _create_validator().validate(raise_if_nullable_id, pull_repository)
