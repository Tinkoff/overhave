import logging
from typing import Dict, List, Optional

from _pytest.main import Session

from overhave.entities import FeatureTypeName, OverhaveFileSettings, StepPrefixesModel
from overhave.testing.settings import OverhaveProjectSettings
from overhave.testing.step_collector import StepCollector
from overhave.testing.test_runner import PytestRunner

logger = logging.getLogger(__name__)


class NullableEntitiesError(Exception):
    """ Application error for situation with unresolved entities. """


class ConfigInjector:
    """ Special class to operate with pytest entites, for example get data and patch objects. """

    def __init__(self) -> None:
        self._project_settings: Optional[OverhaveProjectSettings] = None
        self._step_collector: Optional[StepCollector] = None
        self._test_runner: Optional[PytestRunner] = None
        self._file_settings: Optional[OverhaveFileSettings] = None
        self._feature_types: Optional[List[FeatureTypeName]] = None

        self._current_type: Optional[FeatureTypeName] = None
        self._steps: Dict[FeatureTypeName, Dict[str, List[str]]] = {}

        self._initialized = False

    @staticmethod
    def patch_pytestbdd_prefixes(custom_step_prefixes: Optional[StepPrefixesModel]) -> None:
        """ Def for patch pytestbdd STEP_PREFIXES. """
        if custom_step_prefixes is not None:
            step_prefixes = custom_step_prefixes.extend_defaults()
            logger.debug("Successfully extended pytestbdd step prefixes with custom prefixes:\n%s", step_prefixes)

    def supplement_on_fly(
        self,
        project_settings: OverhaveProjectSettings,
        file_settings: OverhaveFileSettings,
        step_collector: StepCollector,
        test_runner: PytestRunner,
        feature_types: List[FeatureTypeName],
    ) -> None:
        """ Def for dynamical supplement of settings on-the-fly (strictly after PyTest configuring). """
        self._project_settings = project_settings
        self._step_collector = step_collector
        self._test_runner = test_runner
        self._file_settings = file_settings
        self._feature_types = feature_types

        self._steps.update({feature_type: {} for feature_type in self._feature_types})

    def collect_configs(self) -> None:
        """ Special def for pytest run in collect-only mode. Collects pytestbdd steps and other config data. """
        if self._feature_types is None or self._test_runner is None or self._file_settings is None:
            raise NullableEntitiesError
        if not self._initialized:
            logger.info("Started initialization process...")
            for feature_type in self._feature_types:
                self._current_type = feature_type
                self._test_runner.collect_only(
                    fixture_file=(
                        self._file_settings.fixtures_base_dir
                        / self._file_settings.fixtures_file_template_mask.format(feature_type=feature_type)
                    ),
                )
            self._current_type = None
            logger.info("Successfully initialized.")
            self._initialized = True

    @property
    def _inside_collecting(self) -> bool:
        return self._current_type is not None and not self._initialized

    def _load_from_session(self, session: Session) -> None:
        """ Loads pytestbdd steps and other config data from pytest Session. """
        if self._step_collector is None:
            raise NullableEntitiesError
        if self._inside_collecting:
            step_fixtures = self._step_collector.get_pytestbdd_steps(session)
            steps_dict = self._step_collector.compile_steps_dict(step_fixtures)
            if steps_dict:
                logger.debug("Loaded steps dict:\n%s", steps_dict)
            self._steps[self._current_type] = steps_dict  # type: ignore

    def adapt(self, session: Session) -> None:
        """ Main def for data loading from pytest Session and enrichment of pytest configs. """
        if self._inside_collecting:
            self._load_from_session(session)

    def get_steps(self, feature_type: FeatureTypeName) -> Dict[str, List[str]]:
        return self._steps.get(feature_type, {})
