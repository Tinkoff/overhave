import enum


class TestRunStatus(str, enum.Enum):
    """ Enum for test run statuses. """

    STARTED = 'STARTED'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


class EmulationStatus(str, enum.Enum):
    """ Enum for emulation statuses. """

    CREATED = 'CREATED'
    REQUESTED = 'REQUESTED'
    READY = 'READY'
    ERROR = 'ERROR'

    @property
    def processed(self) -> bool:
        return self in (EmulationStatus.READY, EmulationStatus.ERROR)
