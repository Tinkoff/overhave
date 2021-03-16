import click

from demo.settings import OverhaveDemoSettings
from overhave import OverhaveContext, OverhaveLanguageSettings, overhave_factory
from overhave.cli.admin import _run_admin
from overhave.extra import RUSSIAN_PREFIXES


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def overhave_demo() -> None:
    pass


def _set_custom_context() -> None:
    # context enriched with russian `pytest_bdd` prefixes
    context = OverhaveContext(language_settings=OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES))
    overhave_factory().set_context(context)


def _run_demo_admin() -> None:
    demo_settings = OverhaveDemoSettings()
    demo_settings.enrich_env()
    _set_custom_context()
    _run_admin(port=8076, debug=True)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
def admin() -> None:
    _run_demo_admin()
