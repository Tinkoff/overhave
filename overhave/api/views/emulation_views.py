import logging
from typing import List

import fastapi

from overhave.api.deps import get_emulation_storage
from overhave.storage import EmulationRunModel, IEmulationStorage

logger = logging.getLogger(__name__)


def emulation_run_list_handler(
    test_user_id: int,
    emulation_storage: IEmulationStorage = fastapi.Depends(get_emulation_storage),
) -> List[EmulationRunModel]:
    logger.info("Getting %s list with test_user_id=%s...", EmulationRunModel.__name__, test_user_id)
    return emulation_storage.get_emulation_runs_by_test_user_id(test_user_id=test_user_id)
