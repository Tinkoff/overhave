import click

from overhave.base_settings import DataBaseSettings
from overhave.cli.group import overhave


@overhave.command(short_help='Run Overhave web-service')
@click.option('--port', default=8076)
def admin(port: int) -> None:
    """ Run Overhave web-service. """
    from overhave.admin import overhave_app

    DataBaseSettings().setup_db()

    overhave_app().run(host='0.0.0.0', port=port, debug=True)
