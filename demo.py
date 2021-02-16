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
    def check_existence(cls, v: Path):
        if not v.exists():
            raise ValueError(f"Could not find docs directory: '{v}'!")
        return v

    @property
    def features_base_dir(self) -> Path:
        return self.docs_dir / "includes" / "features_structure_example"

    def enrich_env(self) -> None:
        environ[self.__config__.env_prefix + "features_base_dir"] = self.features_base_dir.as_posix()


@click.group(context_settings={'help_option_names': ['-h', '--help']})
def overhave_demo() -> None:
    pass


@overhave_demo.command(short_help='Run Overhave web-service in demo mode')
def admin() -> None:
    demo_settings = OverhaveDemoSettings()
    demo_settings.enrich_env()
    _run_admin(port=8076, debug=True)
