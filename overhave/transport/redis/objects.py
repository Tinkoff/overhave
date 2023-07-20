import abc
import enum
import json
from typing import Any, TypeVar

from pydantic.main import BaseModel


class RedisStream(enum.StrEnum):
    """Enum that declares Redis streams."""

    TEST = "test"
    PUBLICATION = "publication"
    EMULATION = "emulation"

    @property
    def with_dunder(self) -> str:
        return self.value.replace("-", "_")


class _IRedisTask(BaseModel, abc.ABC):
    @property
    @abc.abstractmethod
    def message(self) -> dict[bytes, bytes]:
        pass


class BaseRedisTask(_IRedisTask):
    """Base task for Redis streams."""

    data: BaseModel

    @property
    def message(self) -> dict[bytes, bytes]:
        return {b"data": self.data.model_dump_json().encode("utf-8")}


class TestRunData(BaseModel):
    """Specific data for test run."""

    __test__ = False

    test_run_id: int


class TestRunTask(BaseRedisTask):
    """Redis stream task for test run."""

    __test__ = False

    data: TestRunData


class PublicationData(BaseModel):
    """Specific data for test run."""

    draft_id: int


class PublicationTask(BaseRedisTask):
    """Redis stream task for test run."""

    data: PublicationData


class EmulationData(BaseModel):
    """Specific data for emulation run."""

    emulation_run_id: int


class EmulationTask(BaseRedisTask):
    """Redis stream task for emulation run."""

    data: EmulationData


TRedisTask = TypeVar("TRedisTask", TestRunTask, EmulationTask, PublicationTask, covariant=True)
AnyRedisTask = TestRunTask | PublicationTask | EmulationTask


class RedisPendingData(BaseModel):
    """Class that describes pending data from Redis stream."""

    message_id: str
    consumer: str
    time_since_delivered: int
    times_delivered: int


class RedisUnreadData:
    """Class for unread data from Redis stream."""

    def __init__(self, message_id: bytes, message: dict[bytes, bytes]) -> None:
        self.message_id = message_id.decode()
        self.message = message

    @property
    def decoded_message(self) -> dict[str, Any]:
        return {key.decode(): json.loads(value.decode("utf-8")) for key, value in self.message.items()}

    def __str__(self) -> str:
        return f"{RedisUnreadData.__name__}(id={self.message_id}, message='{self.message}')"


class RedisContainer(BaseModel):
    """Class for parsing instance of :class:`RedisUnreadData` from Redis stream.

    ```task``` will be parsed to one of declared models.
    """

    task: AnyRedisTask
