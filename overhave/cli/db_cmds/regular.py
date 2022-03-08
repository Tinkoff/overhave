import sqlalchemy_utils as sau
import typer
from alembic.config import Config
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError

from overhave import db as database
from overhave.base_settings import DataBaseSettings


def create_schema(config: Config) -> None:
    typer.echo("Creating...")
    config.attributes["metadata"].create_all()
    typer.secho("Completed.", fg="green")


def drop_schema(config: Config) -> None:
    typer.echo("Dropping...")
    meta = config.attributes["metadata"]
    engine = config.attributes["engine"]
    for table in meta.tables:
        engine.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
    engine.execute("DROP TABLE IF EXISTS alembic_version")
    engine.execute("DROP SCHEMA IF EXISTS huey")
    meta.drop_all()
    typer.secho("Completed.", fg="green")


def _ensure_database_exists(db_url: URL) -> None:
    try:
        if not sau.database_exists(db_url):
            sau.create_database(db_url)
    except OperationalError as e:
        typer.echo(e)
        typer.echo("Catched error when trying to check database existence!")


def set_config_to_context(context: typer.Context, settings: DataBaseSettings) -> None:
    """Set Alembic config to Typer context for easy operations and migrations ability."""
    _ensure_database_exists(settings.db_url)
    settings.setup_db()
    config = Config()
    config.attributes["engine"] = settings.create_engine()
    config.attributes["metadata"] = database.metadata
    context.obj = config
