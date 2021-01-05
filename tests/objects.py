from typing import NamedTuple, NewType

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine


class DataBaseContext(NamedTuple):
    metadata: MetaData
    engine: Engine


XDistWorkerValueType = NewType('XDistWorkerValueType', str)
XDistMasterWorker = XDistWorkerValueType("master")
