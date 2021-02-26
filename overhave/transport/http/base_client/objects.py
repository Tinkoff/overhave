import enum


class HttpMethod(str, enum.Enum):
    """ HTTP methods enum. """

    GET = "get"
    POST = "post"
