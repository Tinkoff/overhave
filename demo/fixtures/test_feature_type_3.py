from pytest_bdd import given, scenarios, then, when

from demo.fixtures.parser import step_with_args

scenarios("../features_structure_example/feature_type_3")


@given("Я клиент банка")
def set_client(name: str) -> None:
    pass


@when(step_with_args("я надиктовываю {phrase:Str}"))
def when_user_say(phrase: str):
    pass


@then(step_with_args("бот говорит {phrase:Str}"))
def then_bot_responds(phrase: str):
    pass


@then("бот показывает виджет")
def then_bot_shows_widget():
    pass
