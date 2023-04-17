from pytest_bdd import then

from demo.steps.parser import step_with_args
from overhave import public_step


@public_step
@then(step_with_args("bot responds {phrase:Str}"))
def then_bot_responds(phrase: str) -> None:
    """Then bot responds certain phrase."""


@public_step
@then("bot shows widget")
def then_bot_shows_widget():
    """Then bot shows widget."""
