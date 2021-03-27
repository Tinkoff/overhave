from pytest_bdd import when

from demo.steps.parser import step_with_args


@when("got through")
def when_got_through():
    pass


@when(step_with_args("I say {phrase:Str}"))
def when_user_say(phrase: str) -> None:
    pass


@when("I hang up")
def when_user_hangup():
    pass
