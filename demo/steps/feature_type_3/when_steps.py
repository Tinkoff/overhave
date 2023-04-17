from pytest_bdd import when

from demo.steps.parser import step_with_args
from overhave import public_step


@public_step
@when(step_with_args("я надиктовываю {phrase:Str}"))
def when_user_say(phrase: str) -> None:
    """Когда я надиктовываю конкретную фразу."""
