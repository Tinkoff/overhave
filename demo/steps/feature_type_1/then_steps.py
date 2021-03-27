from pytest_bdd import then

from demo.steps.parser import step_with_args


@then(step_with_args("bot says {phrase:Str}"))
def then_bot_says(phrase: str) -> None:
    pass


@then("call ends")
def then_call_ends():
    pass
