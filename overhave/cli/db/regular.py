import click
import sqlalchemy_utils as sau
from alembic.config import Config
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError

from overhave import db as database
from overhave.base_settings import DataBaseSettings


@click.command(short_help='Create all metadata tables')
@click.pass_obj
def create_all(config: Config) -> None:
    """ Create all metadata tables. """
    click.echo('creating')
    config.attributes["metadata"].create_all()
    click.echo('complete!')


@click.command(short_help='Drop all metadata tables, attributes, schema')
@click.pass_obj
def drop_all(config: Config) -> None:
    """ Drop all metadata tables, attributes, schema. """
    click.confirm('it really need?', abort=True)
    click.echo('dropping')
    meta = config.attributes["metadata"]
    engine = config.attributes["engine"]
    for table in meta.tables:
        engine.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
    engine.execute('DROP TABLE IF EXISTS alembic_version')
    engine.execute('DROP SCHEMA IF EXISTS huey')
    meta.drop_all()
    click.echo('complete!')


def _ensure_database_exists(db_url: URL) -> None:
    try:
        if not sau.database_exists(db_url):
            sau.create_database(db_url)
    except OperationalError as e:
        click.echo(e)
        click.echo("Catched error when trying to check database existence!")


def set_config_to_context(context: click.Context, settings: DataBaseSettings) -> None:
    """ Set Alembic config to Click context for easy operations and migrations ability. """
    _ensure_database_exists(settings.db_url)
    settings.setup_db()
    config = Config()
    config.attributes["engine"] = settings.create_engine()
    config.attributes["metadata"] = database.metadata
    context.obj = config
