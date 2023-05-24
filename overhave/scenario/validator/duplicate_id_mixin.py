import logging
from functools import cached_property
from pathlib import Path

from overhave.scenario.validator.errors import DuplicateFeatureIDError

logger = logging.getLogger(__name__)


class FeatureDuplicatedIdValidationMixin:
    """Class for features validation."""

    @cached_property
    def _feature_id_to_path_mapping(self) -> dict[int, list[Path]]:
        return {}

    def _save_to_feature_id_to_path_mapping(self, feature_path: Path, feature_id: int | None) -> None:
        if not isinstance(feature_id, int):
            return
        if not self._feature_id_to_path_mapping.get(feature_id):
            self._feature_id_to_path_mapping[feature_id] = [feature_path]
            return
        logger.warning("Found duplicate ID=%s!", feature_id)
        self._feature_id_to_path_mapping[feature_id].append(feature_path)

    def _validate_duplicate_ids(self) -> None:
        duplicate_feature_ids = [
            feature_id
            for feature_id, feature_paths in self._feature_id_to_path_mapping.items()
            if len(feature_paths) > 1
        ]
        if not duplicate_feature_ids:
            return
        txt = "Features with duplicate IDs:\n"
        raise DuplicateFeatureIDError(
            txt
            + "\n".join(
                "id={} - {}".format(x, [path.as_posix() for path in self._feature_id_to_path_mapping[x]])
                for x in duplicate_feature_ids
            )
        )
