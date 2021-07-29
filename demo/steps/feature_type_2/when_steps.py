from pytest_bdd import when

from demo.steps.parser import step_with_args


@when(step_with_args("I say {phrase:Str}"))
def when_user_say(phrase: str) -> None:
    """ When user says certain phrase. """
