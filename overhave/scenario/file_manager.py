import logging
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from overhave.entities.converters import ProcessingContext
from overhave.entities.feature import IFeatureExtractor
from overhave.entities.settings import OverhaveFileSettings, OverhaveLanguageSettings
from overhave.scenario.compiler import ScenarioCompiler
from overhave.scenario.parser import ScenarioParser
from overhave.testing.settings import OverhaveProjectSettings

logger = logging.getLogger(__name__)


class FileSavingMixin:
    """ Mixin for files saving. """

    @staticmethod
    def _write_data(file: Any, data: str, entity_name: str) -> None:
        file.write(data)
        file.flush()
        logger.debug("Generated %s file: '%s'", entity_name, file.name)
        assert Path(file.name).exists(), f"{entity_name.upper()} file not created!"

    @staticmethod
    def _get_feature_name(feature_name: str, feature_id: int) -> str:
        return f"{feature_name}_id{feature_id}"


class FileManager(FileSavingMixin):
    """ Class for feature files management. """

    def __init__(
        self,
        project_settings: OverhaveProjectSettings,
        file_settings: OverhaveFileSettings,
        language_settings: OverhaveLanguageSettings,
        feature_extractor: IFeatureExtractor,
        scenario_compiler: ScenarioCompiler,
        scenario_parser: ScenarioParser,
    ):
        self._language_settings = language_settings
        self._project_settings = project_settings
        self._file_settings = file_settings
        self._feature_extractor = feature_extractor
        self._scenario_compiler = scenario_compiler
        self._scenario_parser = scenario_parser

    def _compile_feature_file_name_prefix(self, context: ProcessingContext) -> str:
        feature_name = context.feature.name
        if self._language_settings.translit_pack is not None:
            feature_name = self._language_settings.translit_pack.translate(feature_name)
        return self._get_feature_name(feature_name=feature_name, feature_id=context.feature.id)

    @contextmanager
    def tmp_feature_file(self, context: ProcessingContext) -> Iterator:  # type: ignore
        run_prefix = self._compile_feature_file_name_prefix(context)
        logger.debug("Feature prefix: '%s'", run_prefix)
        with tempfile.NamedTemporaryFile(
            dir=self._file_settings.tmp_features_dir,
            prefix=f"{run_prefix}_",
            suffix=self._file_settings.feature_suffix,
            mode="w",
        ) as file:
            data = self._scenario_compiler.compile(context=context)
            logger.debug("Scenario file:\n%s", data)
            self._write_data(file=file, data=data, entity_name='feature')
            yield file

    @contextmanager
    def tmp_fixture_file(self, context: ProcessingContext, feature_file: Any) -> Iterator:  # type: ignore
        with tempfile.NamedTemporaryFile(
            dir=self._file_settings.tmp_fixtures_dir,
            prefix=f"{context.test_run.id}_",
            suffix=self._file_settings.fixture_suffix,
            mode="w",
        ) as file:
            joined_content = "\n".join(self._project_settings.fixture_content)
            data = joined_content.format(feature_file_path=feature_file.name)

            logger.debug("Fixture file:\n%s", data)
            self._write_data(file=file, data=data, entity_name='fixture')
            yield file

    def produce_feature_file(self, context: ProcessingContext) -> Path:
        feature_file_path: Path = (
            self._feature_extractor.feature_type_to_dir_mapping[context.feature.feature_type.name]
            / f"{self._compile_feature_file_name_prefix(context)}{self._file_settings.feature_suffix}"
        )
        if not feature_file_path.exists():
            logger.info("Create feature file '%s' for commit", feature_file_path.as_posix())
            feature_file_path.touch()
        logger.info("Write scenario to feature file '%s'...", feature_file_path.as_posix())
        with feature_file_path.open('w') as feature_file:
            scenario_text = self._scenario_compiler.compile(context=context)
            logger.debug(scenario_text)
            feature_file.write(scenario_text)
        logger.info("Scenario has successfully written")
        return feature_file_path
