from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from flask_admin.contrib.sqla import ModelView
from pydantic import root_validator, validator
from pydantic.datetime_parse import timedelta
from yarl import URL

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities.language import StepPrefixesModel


class OverhaveAdminSettings(BaseOverhavePrefix):
    """Settings for Overhave Flask Admin customization."""

    # Path to custom index template. By default, contains Overhave project info.
    index_template_path: Optional[Path]

    # Custom SQLAlchemy ModelViews for Overhave admin panel
    custom_views: Optional[Sequence[ModelView]]

    # Enable testing with test execution consumer, based on Redis tasks. Enabled by default.
    # When disabled - all test runs will be executed with :class:`Threadpool`.
    consumer_based: bool = True

    # Threadpool size for admin service
    threadpool_process_num: int = 5


class OverhaveLanguageSettings(BaseOverhavePrefix):
    """Settings for language definitions."""

    step_prefixes: Optional[StepPrefixesModel]


class OverhaveFileSettings(BaseOverhavePrefix):
    """Settings for scenario file savings."""

    feature_suffix: str = ".feature"
    fixture_suffix: str = ".py"

    # Current workdir, used for :class:`PluginResolver` for creating of relative pytest plugins' paths
    work_dir: Path = Path.cwd()

    # Root project directory with features, fixtures and steps packages
    root_dir: Optional[Path]

    # Base directory for feature files, by default - root_dir / 'features'
    features_dir: Path

    # Base directory for pytest files with template mask, by default - root_dir / 'fixtures'
    fixtures_dir: Path
    # Template mask for fixtures pytest files which contain `feature_type` key
    fixtures_file_template_mask: str = "test_{feature_type}.py"

    # Flag for `steps_dir` validation in case of relating to `work_dir`
    validate_steps_dir: bool = False

    # Base directory for pytest-bdd steps, , by default - root_dir / 'steps'
    steps_dir: Path

    # Temporary directory for scenarios test runs
    tmp_dir: Path = Path("/tmp/overhave")  # noqa: S108

    @root_validator(pre=True)
    def validate_dirs(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        root_dir = values.get("root_dir")
        if root_dir:
            for directory in ("features_dir", "fixtures_dir", "steps_dir"):
                if values.get(directory):
                    continue
                values[directory] = Path(root_dir) / directory.replace("_dir", "")
        return values

    @validator("steps_dir")
    def validate_nesting(cls, v: Path, values: Dict[str, Any]) -> Path:
        validate_steps_dir = values["validate_steps_dir"]
        if validate_steps_dir:
            work_dir: Path = values["work_dir"]
            v.relative_to(work_dir)
        return v

    @property
    def tmp_features_dir(self) -> Path:
        return self.tmp_dir / "features"

    @property
    def tmp_fixtures_dir(self) -> Path:
        return self.tmp_dir / "fixtures"

    @property
    def tmp_reports_dir(self) -> Path:
        return self.tmp_dir / "reports"


class OverhaveReportManagerSettings(BaseOverhavePrefix):
    """Settings for :class:`ReportManager`."""

    report_creation_timeout: int = 120  # sec
    report_creation_error_msg: str = "not_created"
    allure_cmdline: str = "allure"
    archive_extension: str = "zip"


class ProcessorSettings(BaseOverhavePrefix):
    """Settings for :class:`Processor`."""

    processes_num: int = 5


class OverhaveRedisSettings(BaseOverhavePrefix):
    """Settings for Redis entities, which use for work with different framework tasks."""

    redis_url: URL = URL("redis://localhost:6379")
    redis_db: int = 0
    redis_block_timeout: timedelta = timedelta(seconds=1)
    redis_read_count: int = 1

    @validator("redis_url", pre=True)
    def validate_url(cls, v: Union[str, URL]) -> URL:
        if isinstance(v, str):
            return URL(v)
        return v

    @property
    def timeout_milliseconds(self) -> int:
        return int(self.redis_block_timeout.total_seconds() * 1000)


class OverhaveEmulationSettings(BaseOverhavePrefix):
    """Settings for Overhave Emulator, which emulates session with test user."""

    # Path for emulation core application, such as GoTTY
    emulation_core_path: str = "/gotty"

    # All emulation core application prefixes for execution
    emulation_prefix: str = "--permit-write --once --address {address} --port {port} --timeout {timeout}"

    # Specific terminal tool startup command with relative `feature_type`, for example: `myapp {feature_type}`
    emulation_base_cmd: Optional[str]
    # Terminal tool command postfix with specified user `name` and `model`, for example: `--name={name} --model={model}`
    # If it is no need in use - may be optional.
    emulation_postfix: Optional[str]

    # Optional additional terminal tool usage description
    emulation_desc_link: Optional[str]

    emulation_bind_ip: str = "0.0.0.0"  # noqa: S104
    # Ports for emulation binding. Expects as string with format `["port1", "port2", ...]`
    emulation_ports: List[int] = [8080]

    # As a real service, should be used follow path: `http://my-service.domain/mount`
    # where `emulation_service_url` = `http://my-service.domain` - URL for service,
    # and `emulation_service_mount` = `mount` - mount point for service redirection.
    # If `emulation_service_mount` is `None` - this is localhost debug.
    emulation_service_url: URL = URL("http://localhost")
    emulation_service_mount: Optional[str]

    # Wait until emulation become served
    emulation_wait_timeout: timedelta = timedelta(seconds=300)

    @validator("emulation_service_url", pre=True)
    def validate_url(cls, v: Union[str, URL]) -> URL:
        if isinstance(v, str):
            return URL(v)
        return v

    @validator("emulation_ports", pre=True)
    def validate_ports(cls, v: Union[List[int], str]) -> List[int]:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",")]
        return v

    def get_emulation_url(self, port: str) -> str:
        if isinstance(self.emulation_service_mount, str):
            return (
                self.emulation_service_url / self.emulation_service_mount / port / ""
            ).human_repr()  # NGINX should redirect to `service:port` by mount point and specified port
        return self.emulation_service_url.with_port(int(port)).human_repr()  # only for local debug

    @property
    def wait_timeout_seconds(self) -> int:
        return int(self.emulation_wait_timeout.total_seconds())

    @property
    def enabled(self) -> bool:
        return isinstance(self.emulation_base_cmd, str)


class OverhaveStepContextSettings(BaseOverhavePrefix):
    """Settings for :class:`StepContextRunner`."""

    step_context_logs: bool = False


class OverhaveDescriptionManagerSettings(BaseOverhavePrefix):
    """Settings for DescriptionManager, which sets the description to Allure report dynamically after test."""

    blocks_delimiter: str = ""
    html: bool = True
