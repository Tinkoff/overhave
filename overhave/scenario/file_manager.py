import logging
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from overhave.entities import IFeatureExtractor, OverhaveFileSettings, TestExecutorContext
from overhave.scenario.compiler import ScenarioCompiler
from overhave.test_execution.settings import OverhaveProjectSettings

logger = logging.getLogger(__name__)


class FileSavingMixin:
    """Mixin for files saving."""

    @staticmethod
    def _write_data(file: tempfile._TemporaryFileWrapper, data: str, entity_name: str) -> None:  # type: ignore
        file.write(data)
        file.flush()
        logger.debug("Generated %s file: '%s'", entity_name, file.name)
        assert Path(file.name).exists(), f"{entity_name.upper()} file not created!"


class FileManager(FileSavingMixin):
    """Class for feature files management."""

    def __init__(
        self,
        project_settings: OverhaveProjectSettings,
        file_settings: OverhaveFileSettings,
        feature_extractor: IFeatureExtractor,
        scenario_compiler: ScenarioCompiler,
    ):
        self._project_settings = project_settings
        self._file_settings = file_settings
        self._feature_extractor = feature_extractor
        self._scenario_compiler = scenario_compiler

    @contextmanager
    def tmp_feature_file(
        self, context: TestExecutorContext
    ) -> Iterator[tempfile._TemporaryFileWrapper]:  # type: ignore
        file_name = Path(context.feature.file_path).name
        logger.debug("Feature file name: '%s'", file_name)
        with tempfile.NamedTemporaryFile(
            dir=self._file_settings.tmp_features_dir,
            prefix=f"{file_name}_id{context.feature.id}",
            suffix=self._file_settings.feature_suffix,
            mode="w",
        ) as file:
            data = self._scenario_compiler.compile(context=context)
            logger.debug("Scenario file:\n%s", data)
            self._write_data(file=file, data=data, entity_name="feature")
            yield file

    @contextmanager
    def tmp_fixture_file(
        self, context: TestExecutorContext, feature_file: tempfile._TemporaryFileWrapper  # type: ignore
    ) -> Iterator[tempfile._TemporaryFileWrapper]:  # type: ignore
        with tempfile.NamedTemporaryFile(
            dir=self._file_settings.tmp_fixtures_dir,
            prefix=f"{context.test_run.id}_",
            suffix=self._file_settings.fixture_suffix,
            mode="w",
        ) as file:
            joined_content = "\n".join(self._project_settings.fixture_content)
            data = joined_content.format(feature_file_path=feature_file.name)

            logger.debug("Fixture file:\n%s", data)
            self._write_data(file=file, data=data, entity_name="fixture")
            yield file

    def produce_feature_file(self, context: TestExecutorContext) -> Path:
        feature_file_path = (
            self._feature_extractor.feature_type_to_dir_mapping[context.feature.feature_type.name]
            / context.feature.file_path
        )
        logger.info("Write scenario to feature file '%s'...", feature_file_path.as_posix())

        scenario_text = self._scenario_compiler.compile(context=context)
        logger.debug(scenario_text)
        feature_file_path.parent.mkdir(parents=True, exist_ok=True)
        feature_file_path.write_text(scenario_text)

        logger.info("Scenario has successfully written")
        return feature_file_path
