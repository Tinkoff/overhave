from pytest_bdd import given, scenarios

from demo.fixtures.parser import step_with_args

scenarios("../features_structure_example/feature_type_1")


@given(step_with_args("application {name:Str}"))
def set_application(name: str) -> None:
    pass
