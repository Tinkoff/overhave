from os import environ
from pathlib import Path

from overhave.base_settings import BaseOverhavePrefix


class OverhaveDemoSettings(BaseOverhavePrefix):
    """ Settings for application demo mode configuration. """

    demo_dir: Path = Path(__file__).parent

    @property
    def project_dir(self) -> Path:
        return self.demo_dir.parent

    @property
    def features_base_dir(self) -> Path:
        return self.demo_dir / "features_structure_example"

    @property
    def fixtures_base_dir(self) -> Path:
        return self.demo_dir / "fixtures"

    @property
    def steps_base_dir(self) -> Path:
        return self.demo_dir / "steps"

    @property
    def _prefix(self) -> str:
        return self.__config__.env_prefix

    def _get_variable(self, name: str) -> str:
        return (self._prefix + name).upper()

    def enrich_env(self) -> None:
        environ[self._get_variable("features_base_dir")] = self.features_base_dir.as_posix()
        environ[self._get_variable("fixtures_base_dir")] = self.fixtures_base_dir.as_posix()
        environ[self._get_variable("steps_base_dir")] = self.steps_base_dir.as_posix()
        environ[self._get_variable("pytest_rootdir")] = self.project_dir.as_posix()

        environ[self._get_variable("stash_url")] = "https://overhave.readthedocs.io"
        environ[self._get_variable("stash_auth_token")] = "secret_token"
        environ[self._get_variable("repository_name")] = "bdd-features"
        environ[self._get_variable("project_key")] = "OVH"
