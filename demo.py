from os import environ
from pathlib import Path

import click
from pydantic import validator

from overhave.base_settings import BaseOverhavePrefix
from overhave.cli.admin import _run_admin


class OverhaveDemoSettings(BaseOverhavePrefix):
    """ Settings for application demo mode configuration. """

    docs_dir: Path = Path(__file__).parent / "docs"

    @validator("docs_dir")
    def check_existence(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Could not find docs directory: '{v}'!")
        return v

    @property
    def features_base_dir(self) -> Path:
        return self.docs_dir / "includes" / "features_structure_example"

    @property
    def _prefix(self) -> str:
        return self.__config__.env_prefix

    def enrich_env(self) -> None:
        environ[self._prefix + "features_base_dir"] = self.features_base_dir.as_posix()
        environ[self._prefix + "stash_url"] = "https://overhave.readthedocs.io"
        environ[self._prefix + "auth_token"] = "secret_token"
        environ[self._prefix + "repository_name"] = "bdd-features"
        environ[self._prefix + "project_key"] = "OVH"


@click.group(context_settings={'help_option_names': ['-h', '--help']})
def overhave_demo() -> None:
    pass


@overhave_demo.command(short_help='Run Overhave web-service in demo mode')
def admin() -> None:
    demo_settings = OverhaveDemoSettings()
    demo_settings.enrich_env()
    _run_admin(port=8076, debug=True)
