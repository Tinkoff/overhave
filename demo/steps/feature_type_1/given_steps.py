from pytest_bdd import given

from demo.steps.parser import step_with_args


@given(step_with_args("application {name:Str}"))
def set_application(name: str) -> None:
    """ Set special application name. """


@given(step_with_args("call from {source_number:Str} to {target_number:Str}"))
def set_call_numbers(source_number: str, target_number: str) -> None:
    """ Set special call numbers. """
