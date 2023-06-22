import enum

from pydantic.env_settings import BaseSettings


class MetricSettings(BaseSettings):
    """Settings for defining metrics container type."""

    class Type(enum.StrEnum):
        COMMON = "COMMON"
        TEST = "TEST"
        EMULATION = "EMULATION"
        PUBLICATION = "PUBLICATION"

    type: Type = Type.COMMON

    class Config:
        env_prefix = "OVERHAVE_METRIC_CONTAINER_"
