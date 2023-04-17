from pytest_bdd import then

from demo.steps.parser import step_with_args
from overhave import public_step


@public_step
@then(step_with_args("bot says {phrase:Str}"))
def then_bot_says(phrase: str) -> None:
    """Then bot says certain phrase."""


@public_step
@then("call ends")
def then_call_ends():
    """Then call ends."""
