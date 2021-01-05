import abc
import enum
import json
from typing import Any, Dict, TypeVar, Union, cast

from pydantic.main import BaseModel


class RedisStream(str, enum.Enum):
    TEST = "test-stream"
    EMULATION = "emulation-stream"

    @property
    def with_dunder(self) -> str:
        return cast(str, self.value.replace("-", "_"))


class IRedisTask(BaseModel, abc.ABC):
    @property
    @abc.abstractmethod
    def message(self) -> Dict[bytes, bytes]:
        pass


class BaseRedisTask(IRedisTask):
    data: Any

    @property
    def message(self) -> Dict[bytes, bytes]:
        return {b'data': self.data.json().encode('utf-8')}


class TestRunData(BaseModel):
    test_run_id: int


class TestRunTask(BaseRedisTask):
    data: TestRunData


class EmulationData(BaseModel):
    emulation_run_id: int


class EmulationTask(BaseRedisTask):
    data: EmulationData


TRedisTask = TypeVar('TRedisTask', TestRunTask, EmulationTask, covariant=True)
AnyRedisTask = Union[TestRunTask, EmulationTask]


class RedisPendingData(BaseModel):
    message_id: str
    consumer: str
    time_since_delivered: int
    times_delivered: int


class RedisUnreadData:
    def __init__(self, message_id: bytes, message: Dict[bytes, bytes]) -> None:
        self.message_id = message_id.decode()
        self.message = message

    @property
    def decoded_message(self) -> Dict[str, Any]:
        return {key.decode(): json.loads(value.decode('utf-8')) for key, value in self.message.items()}


class RedisContainer(BaseModel):
    task: AnyRedisTask
