from pytest_bdd import given, scenarios, then, when

from demo.fixtures.parser import step_with_args

scenarios("../features_structure_example/feature_type_2")


@given("I am bank client")
def set_client(name: str) -> None:
    pass


@when(step_with_args("I say {phrase:Str}"))
def when_user_say(phrase: str):
    pass


@then(step_with_args("bot responds {phrase:Str}"))
def then_bot_responds(phrase: str):
    pass


@then("bot shows widget")
def then_bot_shows_widget():
    pass
