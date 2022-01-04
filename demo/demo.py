from unittest import mock

import click

from demo.settings import OverhaveDemoAppLanguage, OverhaveDemoSettingsGenerator
from overhave import (
    OverhaveAdminContext,
    OverhavePublicationContext,
    OverhaveRedisStream,
    OverhaveTestExecutionContext,
    db,
    overhave_admin_factory,
    overhave_publication_factory,
    overhave_synchronizer_factory,
    overhave_test_execution_factory,
)
from overhave.cli.admin import _get_admin_app
from overhave.cli.consumers import _run_consumer
from overhave.cli.synchronization import _create_synchronizer
from overhave.factory import OverhaveSynchronizerContext


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def overhave_demo() -> None:
    pass


def _get_overhave_settings_generator(language: str, threadpool: bool = False) -> OverhaveDemoSettingsGenerator:
    return OverhaveDemoSettingsGenerator(language=OverhaveDemoAppLanguage(language), threadpool=threadpool)


def _prepare_test_execution_factory(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    test_execution_context: OverhaveTestExecutionContext = OverhaveTestExecutionContext(
        **settings_generator.default_context_settings  # type: ignore
    )
    overhave_test_execution_factory().set_context(test_execution_context)


def _prepare_publication_factory(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    publication_context: OverhavePublicationContext = OverhavePublicationContext(
        **settings_generator.publication_context_settings  # type: ignore
    )
    overhave_publication_factory().set_context(publication_context)


def _prepare_synchronizer_factory(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    synchronizer_context: OverhaveSynchronizerContext = OverhaveSynchronizerContext(
        **settings_generator.default_context_settings  # type: ignore
    )
    overhave_synchronizer_factory().set_context(synchronizer_context)


def _ensure_demo_app_has_features() -> None:
    with db.create_session() as session:
        create_db_features = not bool(session.query(db.Feature).all())
    with mock.patch("git.Repo", return_value=mock.MagicMock()):
        _create_synchronizer().synchronize(create_db_features=create_db_features)


def _run_demo_admin(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    context = OverhaveAdminContext(**settings_generator.admin_context_settings)  # type: ignore
    overhave_admin_factory().set_context(context)
    if not context.admin_settings.consumer_based:
        _prepare_test_execution_factory(settings_generator)
        _prepare_publication_factory(settings_generator)
    _prepare_synchronizer_factory(settings_generator)
    demo_admin_app = _get_admin_app()
    _ensure_demo_app_has_features()
    demo_admin_app.run(host="localhost", port=8076, debug=True)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
@click.option(
    "-l",
    "--language",
    default=OverhaveDemoAppLanguage.RU.value,
    help="Overhave application language (defines step prefixes only right now)",
)
@click.option(
    "-t",
    "--threadpool",
    is_flag=True,
    help="Run Overhave admin without consumers, which produces tasks into Threadpool",
)
def admin(threadpool: bool, language: str) -> None:
    _run_demo_admin(settings_generator=_get_overhave_settings_generator(language=language, threadpool=threadpool))


def _run_demo_consumer(stream: OverhaveRedisStream, settings_generator: OverhaveDemoSettingsGenerator) -> None:
    if stream is OverhaveRedisStream.TEST:
        _prepare_test_execution_factory(settings_generator)
    if stream is OverhaveRedisStream.PUBLICATION:
        _prepare_publication_factory(settings_generator)
    _run_consumer(stream=stream)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
@click.option(
    "-l",
    "--language",
    default=OverhaveDemoAppLanguage.RU.value,
    help="Overhave application language (defines step prefixes only right now)",
)
@click.option(
    "-s",
    "--stream",
    type=click.Choice(OverhaveRedisStream.__members__),
    callback=lambda c, p, v: getattr(OverhaveRedisStream, v),
    help="Redis stream, which defines application",
)
def consumer(stream: OverhaveRedisStream, language: str) -> None:
    _run_demo_consumer(stream=stream, settings_generator=_get_overhave_settings_generator(language=language))


@overhave_demo.command(short_help="Run Overhave feature synchronization")
@click.option("-c", "--create-db-features", is_flag=True, help="Create features in database if necessary")
@click.option(
    "-l",
    "--language",
    default=OverhaveDemoAppLanguage.RU.value,
    help="Overhave application language (defines step prefixes only right now)",
)
def synchronize(create_db_features: bool, language: str) -> None:
    _prepare_synchronizer_factory(settings_generator=_get_overhave_settings_generator(language=language))
    _create_synchronizer().synchronize(create_db_features)
