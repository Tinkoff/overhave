import click

from overhave import overhave_app
from overhave.base_settings import DataBaseSettings, LoggingSettings
from overhave.cli.group import overhave
from overhave.factory import get_admin_factory


def _run_admin(port: int, debug: bool) -> None:
    DataBaseSettings().setup_db()
    LoggingSettings().setup_logging()
    overhave_app(get_admin_factory()).run(host="localhost", port=port, debug=debug)


@overhave.command(short_help="Run Overhave web-service")
@click.option("--port", default=8076)
@click.option("--debug", default=False)
def admin(port: int, debug: bool) -> None:
    _run_admin(port, debug)
