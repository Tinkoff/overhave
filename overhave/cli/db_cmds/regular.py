# import sqlalchemy as sa  # noqa: E800
import sqlalchemy.engine
import sqlalchemy_utils as sau
import typer
from alembic.config import Config
from sqlalchemy.exc import OperationalError

from overhave import db
from overhave.base_settings import DataBaseSettings


def create_schema(config: Config) -> None:
    typer.echo("Creating...")
    config.attributes["metadata"].create_all(bind=db.metadata.engine)
    typer.secho("Completed.", fg="green")


def drop_schema(config: Config) -> None:
    typer.echo("Dropping...")
    meta = config.attributes["metadata"]
    engine: sqlalchemy.engine.Engine = config.attributes["engine"]  # SQLAlchemy2.0 - sa.Engine

    connection: sqlalchemy.engine.Connection = engine.connect()  # SQLAlchemy2.0 - sa.Connection
    for table in meta.tables:
        connection.execute(sqlalchemy.text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
    connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS alembic_version"))

    meta.drop_all(engine)
    typer.secho("Completed.", fg="green")


def _ensure_database_exists(db_url: sqlalchemy.engine.URL) -> None:  # SQLAlchemy2.0 - sa.URL
    try:
        if not sau.database_exists(db_url):
            sau.create_database(db_url)
    except OperationalError as e:
        typer.echo(e)
        typer.echo("Catched error when trying to check database existence!")


def set_config_to_context(context: typer.Context, settings: DataBaseSettings) -> None:
    """Set Alembic config to Typer context for easy operations and migrations ability."""
    settings.setup_engine()
    _ensure_database_exists(db.metadata.engine.url)

    config = Config()
    config.attributes["engine"] = db.metadata.engine
    config.attributes["metadata"] = db.metadata
    context.obj = config
