import click

from overhave import overhave_app
from overhave.cli.group import overhave
from overhave.factory import get_proxy_factory


def _run_admin(port: int, debug: bool) -> None:
    factory = get_proxy_factory()
    overhave_app(factory).run(host='0.0.0.0', port=port, debug=debug)


@overhave.command(short_help='Run Overhave web-service')
@click.option('--port', default=8076)
@click.option('--debug', default=False)
def admin(port: int, debug: bool) -> None:
    _run_admin(port, debug)
