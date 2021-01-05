from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import root_validator, validator
from pydantic.datetime_parse import timedelta
from yarl import URL

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities.language import StepPrefixesModel, TranslitPack


class OverhaveScenarioCompilerSettings(BaseOverhavePrefix):
    """ Settings for scenario compiling and parsing. """

    tag_prefix: str = "@"
    created_by_prefix: str = "# created by"
    last_edited_by_prefix: str = "last edited by"
    published_by_prefix: str = "published by"

    last_edited_time_delimiter: str = ","
    blocks_delimiter: str = "|"


class OverhaveLanguageSettings(BaseOverhavePrefix):
    """ Settings for language definitions. """

    step_prefixes: Optional[StepPrefixesModel]
    translit_pack: Optional[TranslitPack]


class OverhaveFileSettings(BaseOverhavePrefix):
    """ Settings for scenario file savings. """

    feature_suffix: str = ".feature"
    fixture_suffix: str = ".py"

    # Base directory where feature files placed
    features_base_dir: Path
    # Base directory where pytest files with template mask placed
    fixtures_base_dir: Path
    # Template mask for fixtures pytest files which contain `feature_type` key
    fixtures_file_template_mask: str = "test_{feature_type}.py"
    # Temporary directory for scenarios test runs
    tmp_dir: Path

    @root_validator(pre=True)
    def validate_fixtures_base_dir(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        fixtures_base_dir = values.get('fixtures_base_dir')
        if fixtures_base_dir:
            values['fixtures_base_dir'] = Path(fixtures_base_dir)
        else:
            features_base_dir = values.get('features_base_dir')
            if not features_base_dir:
                raise ValueError("Could not resolve 'fixtures_base_dir'!")
            values['fixtures_base_dir'] = Path(features_base_dir).parent
        return values

    @property
    def tmp_features_dir(self) -> Path:
        return self.tmp_dir / "features"

    @property
    def tmp_fixtures_dir(self) -> Path:
        return self.tmp_dir / "fixtures"

    @property
    def tmp_reports_dir(self) -> Path:
        return self.tmp_dir / "reports"


class ProcessorSettings(BaseOverhavePrefix):
    """ Settings for Overhave Processor, which processes test requests from front. """

    report_creation_timeout: int = 120  # sec
    processes_num: int = 5
    report_creation_error_msg: str = 'not_created'
    allure_cmdline: str = "/allure/bin/allure"


class OverhaveRedisSettings(BaseOverhavePrefix):
    """ Settings for Redis entities, which use for work with different framework tasks. """

    redis_url: URL = URL("redis://localhost:6379")
    redis_db: int = 0
    redis_block_timeout: timedelta = timedelta(seconds=1)
    redis_read_count: int = 1

    @validator('redis_url', pre=True)
    def validate_url(cls, v: Union[str, URL]) -> URL:
        if isinstance(v, str):
            return URL(v)
        return v

    @property
    def timeout_milliseconds(self) -> int:
        return int(self.redis_block_timeout.total_seconds() * 1000)


class OverhaveEmulationSettings(BaseOverhavePrefix):
    """ Settings for Overhave Emulator, which emulates session with test user. """

    # Path for emulation core application, such as GoTTY
    emulation_core_path: str = "/gotty"

    # All emulation core application prefixes for execution
    emulation_prefix: str = "--permit-write --once --address {address} --port {port} --timeout {timeout}"

    # Specific terminal tool startup command with relative `feature_type`, for example: `myapp {feature_type}`
    emulation_base_cmd: str
    # Terminal tool command postfix with specified user `name` and `model`, for example: `--name={name} --model={model}`
    # If it is no need in use - may be optional.
    emulation_postfix: Optional[str]

    # Optional additional terminal tool usage description
    emulation_desc_link: Optional[str]

    emulation_bind_ip: str = "0.0.0.0"
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

    @validator('emulation_service_url', pre=True)
    def validate_url(cls, v: Union[str, URL]) -> URL:
        if isinstance(v, str):
            return URL(v)
        return v

    @validator('emulation_ports', pre=True)
    def validate_ports(cls, v: Union[List[int], str]) -> List[int]:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",")]
        return v

    def get_emulation_url(self, port: str) -> URL:
        if isinstance(self.emulation_service_mount, str):
            return (
                self.emulation_service_url / self.emulation_service_mount / port / ""
            )  # NGINX should redirect to `service:port` by mount point and specified port
        return self.emulation_service_url.with_port(int(port))  # only for local debug

    @property
    def wait_timeout_seconds(self) -> int:
        return int(self.emulation_wait_timeout.total_seconds())
