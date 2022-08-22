import logging
from typing import List

import fastapi

from overhave.api.deps import get_feature_type_storage
from overhave.storage import FeatureTypeModel, IFeatureTypeStorage

logger = logging.getLogger(__name__)


def feature_types_list_handler(
    feature_type_storage: IFeatureTypeStorage = fastapi.Depends(get_feature_type_storage),
) -> List[FeatureTypeModel]:
    logger.info("Getting %s list...", FeatureTypeModel.__name__)
    return feature_type_storage.get_all_feature_types()
