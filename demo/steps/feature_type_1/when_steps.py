from pytest_bdd import when

from demo.steps.parser import step_with_args
from overhave import public_step


@public_step
@when("got through")
def when_got_through():
    """When call got through."""


@public_step
@when(step_with_args("I say {phrase:Str}"))
def when_user_say(phrase: str) -> None:
    """When user says certain phrase."""


@public_step
@when("I hang up")
def when_user_hangup():
    """When user hangs up."""
