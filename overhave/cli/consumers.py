import click

from overhave.cli.group import overhave
from overhave.factory import ConsumerFactory, get_proxy_factory
from overhave.redis import RedisStream


@overhave.command(short_help='Run Overhave Redis consumer')
@click.option(
    "-s",
    "--stream",
    type=click.Choice(RedisStream.__members__),
    callback=lambda c, p, v: getattr(RedisStream, v),
    help="Redis stream, which defines application",
)
def consumer(stream: RedisStream) -> None:
    """ Run Overhave Redis consumer. """
    factory = get_proxy_factory()
    factory.context.logging_settings.setup_logging()
    ConsumerFactory(factory=factory, stream=stream).runner.run()
