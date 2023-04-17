from pytest_bdd import given

from overhave.test_execution import public_step


@public_step
@given("I am bank client")
def set_client() -> None:
    """Set client."""
