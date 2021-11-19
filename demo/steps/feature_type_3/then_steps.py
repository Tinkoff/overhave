from pytest_bdd import then

from demo.steps.parser import step_with_args


@then(step_with_args("бот говорит {phrase:Str}"))
def then_bot_responds(phrase: str) -> None:
    """Тогда бот говорит конкретную фразу."""


@then("бот показывает виджет")
def then_bot_shows_widget():
    """Тогда бот показывает виджет."""
