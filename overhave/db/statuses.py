import enum


class TestRunStatus(str, enum.Enum):
    STARTED = 'STARTED'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


class EmulationStatus(str, enum.Enum):
    CREATED = 'CREATED'
    REQUESTED = 'REQUESTED'
    READY = 'READY'
    ERROR = 'ERROR'

    @property
    def processed(self) -> bool:
        return self in (EmulationStatus.READY, EmulationStatus.ERROR)
