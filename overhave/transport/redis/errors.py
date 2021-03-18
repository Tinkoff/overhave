class BaseRedisException(Exception):
    """ Base exception for RedisProducer. """


class RedisConnectionError(BaseRedisException):
    """ Exception for redis.exceptions.ConnectionError. """
