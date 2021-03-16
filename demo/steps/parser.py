from pytest_bdd import parsers
from pytest_bdd.parsers import parse


def step_with_args(text: str) -> parse:
    return parsers.parse(text, extra_types=dict(Str=str))
