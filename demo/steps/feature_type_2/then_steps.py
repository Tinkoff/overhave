from pytest_bdd import then

from demo.steps.parser import step_with_args


@then(step_with_args("bot responds {phrase:Str}"))
def then_bot_responds(phrase: str):
    pass


@then("bot shows widget")
def then_bot_shows_widget():
    pass
