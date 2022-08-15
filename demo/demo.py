import logging
from contextlib import contextmanager
from typing import Iterator
from unittest import mock

import typer
from pydantic import SecretStr

from demo.settings import OverhaveDemoAppLanguage, OverhaveDemoSettingsGenerator
from overhave import (
    OverhaveAdminContext,
    OverhavePublicationContext,
    OverhaveRedisStream,
    OverhaveSynchronizerContext,
    OverhaveTestExecutionContext,
    db,
    overhave_admin_factory,
    overhave_publication_factory,
    overhave_synchronizer_factory,
    overhave_test_execution_factory,
)
from overhave.cli.admin import _get_admin_app
from overhave.cli.consumers import _run_consumer
from overhave.cli.synchronizer import _create_synchronizer, _create_validator
from overhave.scenario.parser.parser import BaseScenarioParserError

logger = logging.getLogger(__name__)

overhave_demo = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def _get_overhave_settings_generator(
    language: OverhaveDemoAppLanguage,
    threadpool: bool = False,
    admin_host: str = "localhost",
    admin_port: int = 8076,
) -> OverhaveDemoSettingsGenerator:
    return OverhaveDemoSettingsGenerator(
        language=language, threadpool=threadpool, admin_host=admin_host, admin_port=admin_port
    )


def _prepare_test_execution_factory(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    test_execution_context: OverhaveTestExecutionContext = OverhaveTestExecutionContext(
        **settings_generator.test_execution_settings  # type: ignore
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


@contextmanager
def _mock_git_repo() -> Iterator[None]:
    with mock.patch("git.Repo", return_value=mock.MagicMock()):
        yield


def _ensure_demo_app_has_features(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    synchronizer = _create_synchronizer()
    with db.create_session() as session:
        create_db_features = session.query(db.Feature).first() is None
    if not overhave_synchronizer_factory().system_user_storage.get_user_by_credits(
        login=settings_generator.default_feature_user
    ):
        overhave_synchronizer_factory().system_user_storage.create_user(
            login=settings_generator.default_feature_user, password=SecretStr(settings_generator.default_feature_user)
        )
    try:
        synchronizer.synchronize(create_db_features=create_db_features)
    except BaseScenarioParserError:
        logger.exception("Could not create features completely! Skip it.")


def _run_demo_admin(settings_generator: OverhaveDemoSettingsGenerator) -> None:
    context = OverhaveAdminContext(**settings_generator.admin_context_settings)  # type: ignore
    overhave_admin_factory().set_context(context)
    if not context.admin_settings.consumer_based:
        _prepare_test_execution_factory(settings_generator)
        _prepare_publication_factory(settings_generator)
    _prepare_synchronizer_factory(settings_generator)
    demo_admin_app = _get_admin_app()
    with mock.patch("git.Repo", return_value=mock.MagicMock()):
        _ensure_demo_app_has_features(settings_generator)
        demo_admin_app.run(host=settings_generator.admin_host, port=settings_generator.admin_port, debug=True)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
def admin(
    host: str = typer.Option("localhost", "-h", "--host", help="Run Overhave admin with specified host"),
    port: int = typer.Option(8076, "-p", "--port", help="Run Overhave admin with specified port"),
    threadpool: bool = typer.Option(
        False,
        "-t",
        "--threadpool",
        is_flag=True,
        help="Run Overhave admin without consumers, which produces tasks into Threadpool",
    ),
    language: OverhaveDemoAppLanguage = typer.Option(
        OverhaveDemoAppLanguage.RU,
        "-l",
        "--language",
        help="Overhave application language (defines step prefixes only right now)",
    ),
) -> None:
    _run_demo_admin(
        settings_generator=_get_overhave_settings_generator(
            language=language, threadpool=threadpool, admin_host=host, admin_port=port
        )
    )


def _run_demo_consumer(stream: OverhaveRedisStream, settings_generator: OverhaveDemoSettingsGenerator) -> None:
    if stream is OverhaveRedisStream.TEST:
        _prepare_test_execution_factory(settings_generator)
    if stream is OverhaveRedisStream.PUBLICATION:
        _prepare_publication_factory(settings_generator)
    _run_consumer(stream=stream)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
def consumer(
    stream: OverhaveRedisStream = typer.Option(..., "-s", "--stream", help="Redis stream, which defines application"),
    language: OverhaveDemoAppLanguage = typer.Option(
        OverhaveDemoAppLanguage.RU,
        "-l",
        "--language",
        help="Overhave application language (defines step prefixes only right now)",
    ),
) -> None:
    _run_demo_consumer(stream=stream, settings_generator=_get_overhave_settings_generator(language=language))


@overhave_demo.command(short_help="Run Overhave feature synchronization")
def sync_run(
    create_db_features: bool = typer.Option(
        False, "-c", "--create-db-features", is_flag=True, help="Create features in database if necessary"
    ),
    language: OverhaveDemoAppLanguage = typer.Option(
        OverhaveDemoAppLanguage.RU,
        "-l",
        "--language",
        help="Overhave application language (defines step prefixes only right now)",
    ),
) -> None:
    _prepare_synchronizer_factory(settings_generator=_get_overhave_settings_generator(language=language))
    with _mock_git_repo():
        _create_synchronizer().synchronize(create_db_features)


@overhave_demo.command(short_help="Run Overhave feature synchronization")
def validate_features(
    language: OverhaveDemoAppLanguage = typer.Option(
        OverhaveDemoAppLanguage.RU,
        "-l",
        "--language",
        help="Overhave application language (defines step prefixes only right now)",
    ),
    raise_if_nullable_id: bool = typer.Option(
        False, "-r", "--raise-if-nullable-id", is_flag=True, help="Raise if validator find features with nullable IDs"
    ),
) -> None:
    _prepare_synchronizer_factory(settings_generator=_get_overhave_settings_generator(language=language))
    with _mock_git_repo():
        _create_validator().validate(raise_if_nullable_id)
