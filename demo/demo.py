import click

from demo.settings import OverhaveDemoSettingsGenerator
from overhave import (
    OverhaveAdminContext,
    OverhavePublicationContext,
    OverhaveRedisStream,
    OverhaveTestExecutionContext,
    overhave_admin_factory,
    overhave_publication_factory,
    overhave_test_execution_factory,
)
from overhave.cli.admin import _run_admin
from overhave.cli.consumers import _run_consumer

_SETTINGS_GENERATOR = OverhaveDemoSettingsGenerator()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def overhave_demo() -> None:
    pass


def _run_demo_admin() -> None:
    context = OverhaveAdminContext(**_SETTINGS_GENERATOR.default_context_settings)
    overhave_admin_factory().set_context(context)
    _run_admin(port=8076, debug=True)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
def admin() -> None:
    _run_demo_admin()


def _run_demo_consumer(stream: OverhaveRedisStream) -> None:
    if stream is OverhaveRedisStream.TEST:
        context: OverhaveTestExecutionContext = OverhaveTestExecutionContext(
            **_SETTINGS_GENERATOR.default_context_settings
        )
        overhave_test_execution_factory().set_context(context)
    if stream is OverhaveRedisStream.PUBLICATION:
        context: OverhavePublicationContext = OverhavePublicationContext(**_SETTINGS_GENERATOR.publication_settings)
        overhave_publication_factory().set_context(context)
    _run_consumer(stream=stream)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
@click.option(
    "-s",
    "--stream",
    type=click.Choice(OverhaveRedisStream.__members__),
    callback=lambda c, p, v: getattr(OverhaveRedisStream, v),
    help="Redis stream, which defines application",
)
def consumer(stream: OverhaveRedisStream) -> None:
    _run_demo_consumer(stream)
