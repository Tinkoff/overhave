import abc
import enum
import json
from typing import Any, Dict, TypeVar, Union, cast

from pydantic.main import BaseModel


class RedisStream(str, enum.Enum):
    """ Enum that declares Redis streams. """

    TEST = "test-stream"
    EMULATION = "emulation-stream"

    @property
    def with_dunder(self) -> str:
        return cast(str, self.value.replace("-", "_"))


class _IRedisTask(BaseModel, abc.ABC):
    @property
    @abc.abstractmethod
    def message(self) -> Dict[bytes, bytes]:
        pass


class BaseRedisTask(_IRedisTask):
    """ Base task for Redis streams. """

    data: Any

    @property
    def message(self) -> Dict[bytes, bytes]:
        return {b'data': self.data.json().encode('utf-8')}


class TestRunData(BaseModel):
    """ Specific data for test run. """

    test_run_id: int


class TestRunTask(BaseRedisTask):
    """ Redis stream task for test run. """

    data: TestRunData


class EmulationData(BaseModel):
    """ Specific data for emulation run. """

    emulation_run_id: int


class EmulationTask(BaseRedisTask):
    """ Redis stream task for emulation run. """

    data: EmulationData


TRedisTask = TypeVar('TRedisTask', TestRunTask, EmulationTask, covariant=True)


class RedisPendingData(BaseModel):
    """ Class that describes pending data from Redis stream. """

    message_id: str
    consumer: str
    time_since_delivered: int
    times_delivered: int


class RedisUnreadData:
    """ Class for unread data from Redis stream. """

    def __init__(self, message_id: bytes, message: Dict[bytes, bytes]) -> None:
        self.message_id = message_id.decode()
        self.message = message

    @property
    def decoded_message(self) -> Dict[str, Any]:
        return {key.decode(): json.loads(value.decode('utf-8')) for key, value in self.message.items()}


class RedisContainer(BaseModel):
    """ Class for parsing instance of :class:`RedisUnreadData` from Redis stream.

    ```task``` will be parsed to one of declared models.
    """

    task: Union[TestRunTask, EmulationTask]
