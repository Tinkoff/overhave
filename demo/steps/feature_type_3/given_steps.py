from pytest_bdd import given


@given("Я клиент банка")
def set_client() -> None:
    """Спецификация клиента."""
