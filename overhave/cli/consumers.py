import click

from overhave.base_settings import DataBaseSettings, LoggingSettings
from overhave.cli.group import overhave
from overhave.factory import ConsumerFactory
from overhave.transport import RedisStream


def _run_consumer(stream: RedisStream) -> None:
    DataBaseSettings().setup_db()
    LoggingSettings().setup_logging()
    ConsumerFactory(stream=stream).runner.run()


@overhave.command(short_help="Run Overhave Redis consumer")
@click.option(
    "-s",
    "--stream",
    type=click.Choice(RedisStream.__members__),
    callback=lambda c, p, v: getattr(RedisStream, v),
    help="Redis stream, which defines application",
)
def consumer(stream: RedisStream) -> None:
    """ Run Overhave Redis consumer. """
    _run_consumer(stream)
