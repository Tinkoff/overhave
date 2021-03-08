from os import environ
from pathlib import Path

import click

from overhave import OverhaveContext, OverhaveLanguageSettings, OverhaveTestSettings, overhave_factory
from overhave.base_settings import BaseOverhavePrefix
from overhave.cli.admin import _run_admin
from overhave.extra import RUSSIAN_PREFIXES, RUSSIAN_TRANSLIT_PACK


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def overhave_demo() -> None:
    pass


class _OverhaveDemoSettings(BaseOverhavePrefix):
    """ Settings for application demo mode configuration. """

    demo_dir: Path = Path(__file__).parent

    @property
    def features_base_dir(self) -> Path:
        return self.demo_dir / "features_structure_example"

    @property
    def fixtures_base_dir(self) -> Path:
        return self.demo_dir / "fixtures"

    @property
    def _prefix(self) -> str:
        return self.__config__.env_prefix

    def _get_variable(self, name: str) -> str:
        return (self._prefix + name).upper()

    def enrich_env(self) -> None:
        environ[self._get_variable("features_base_dir")] = self.features_base_dir.as_posix()
        environ[self._get_variable("fixtures_base_dir")] = self.fixtures_base_dir.as_posix()
        environ[self._get_variable("stash_url")] = "https://overhave.readthedocs.io"
        environ[self._get_variable("stash_auth_token")] = "secret_token"
        environ[self._get_variable("repository_name")] = "bdd-features"
        environ[self._get_variable("project_key")] = "OVH"


def _set_custom_context() -> None:
    context = OverhaveContext(
        test_settings=OverhaveTestSettings(extra_pytest_addoptions="-p overhave --enable-injection"),
        language_settings=OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES, translit_pack=RUSSIAN_TRANSLIT_PACK),
    )
    overhave_factory().set_context(context)


def _run_demo_admin() -> None:
    demo_settings = _OverhaveDemoSettings()
    demo_settings.enrich_env()
    _set_custom_context()
    _run_admin(port=8076, debug=True)


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
def admin() -> None:
    _run_demo_admin()
