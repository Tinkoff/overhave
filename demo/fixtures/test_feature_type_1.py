from pytest_bdd import given, scenarios, then, when

from demo.fixtures.parser import step_with_args

scenarios("../features_structure_example/feature_type_1")


@given(step_with_args("application {name:Str}"))
def set_application(name: str) -> None:
    pass


@given(step_with_args("call from {source_number:Str} to {target_number:Str}"))
def set_call_numbers(source_number: str, target_number: str) -> None:
    pass


@when("got through")
def when_got_through():
    pass


@when(step_with_args("I say {phrase:Str}"))
def when_user_say(phrase: str):
    pass


@when("I hang up")
def when_user_hangup():
    pass


@then(step_with_args("bot says {phrase:Str}"))
def then_bot_says(phrase: str):
    pass


@then("call ends")
def then_call_ends():
    pass
