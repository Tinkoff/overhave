from pytest_bdd import given

from overhave import public_step


@public_step
@given("Я клиент банка")
def set_client() -> None:
    """Спецификация клиента."""
