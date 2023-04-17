from pytest_bdd import given

from demo.steps.parser import step_with_args
from overhave import public_step


@public_step
@given(step_with_args("application {name:Str}"))
def set_application(name: str) -> None:
    """Set special application name."""


@public_step
@given(step_with_args("call from {source_number:Str} to {target_number:Str}"))
def set_call_numbers(source_number: str, target_number: str) -> None:
    """Set special call numbers."""


@given("not public step")
def not_public_step(source_number: str, target_number: str) -> None:
    # Not public step. You can see all steps if you specified `False` at `demo/settings.py` for
    # `OverhaveStepCollectorSettings.hide_non_public_steps` attribute
    pass
