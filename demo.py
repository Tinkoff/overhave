from contextlib import contextmanager
from os import environ
from pathlib import Path
from typing import Dict, Iterator

import click
from pydantic import validator

from overhave.base_settings import BaseOverhavePrefix
from overhave.cli.admin import _run_admin


class _OverhaveDemoSettings(BaseOverhavePrefix):
    """ Settings for application demo mode configuration. """

    docs_dir: Path = Path(__file__).parent / "docs"

    @validator("docs_dir")
    def check_existence(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Could not find docs directory: '{v}'!")
        return v

    @property
    def includes_dir(self) -> Path:
        return self.docs_dir / "includes"

    @property
    def features_base_dir(self) -> Path:
        return self.includes_dir / "features_structure_example"

    @property
    def _prefix(self) -> str:
        return self.__config__.env_prefix

    def _get_variable(self, name: str) -> str:
        return (self._prefix + name).upper()

    def enrich_env(self) -> None:
        environ[self._get_variable("features_base_dir")] = self.features_base_dir.as_posix()
        environ[self._get_variable("stash_url")] = "https://overhave.readthedocs.io"
        environ[self._get_variable("stash_auth_token")] = "secret_token"
        environ[self._get_variable("repository_name")] = "bdd-features"
        environ[self._get_variable("project_key")] = "OVH"


@contextmanager
def _demo_files_creator(demo_settings: _OverhaveDemoSettings) -> Iterator[None]:
    fixture_files: Dict[str, Path] = {}
    for feature_type_dir in demo_settings.features_base_dir.iterdir():
        if not feature_type_dir.match("feature_type_*"):
            continue
        fixture_files[feature_type_dir.name] = (
            demo_settings.includes_dir / ("test_" + feature_type_dir.name)
        ).with_suffix(".py")

    for feature_type in fixture_files:
        file = fixture_files[feature_type]
        file.write_text("from pytest_bdd import scenarios\n" f"scenarios('{feature_type}')")
        click.secho(f"Created demo pytest file '{file}'.", fg="blue")
    try:
        yield
    finally:
        for file in fixture_files.values():
            if not file.exists():
                continue
            file.unlink()
            click.secho(f"Removed demo pytest file '{file}'.", fg="blue")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def overhave_demo() -> None:
    pass


@overhave_demo.command(short_help="Run Overhave web-service in demo mode")
def admin() -> None:
    demo_settings = _OverhaveDemoSettings()
    demo_settings.enrich_env()
    with _demo_files_creator(demo_settings):
        _run_admin(port=8076, debug=True)
