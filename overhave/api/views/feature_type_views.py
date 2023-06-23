import logging

import fastapi

from overhave.api.deps import get_feature_type_storage
from overhave.storage import FeatureTypeModel, IFeatureTypeStorage

logger = logging.getLogger(__name__)


def feature_types_list_handler(
    feature_type_storage: IFeatureTypeStorage = fastapi.Depends(get_feature_type_storage),
) -> list[FeatureTypeModel]:
    logger.info("Getting %s list...", FeatureTypeModel.__name__)
    return feature_type_storage.all_feature_types
