from _pytest.nodes import Item

from overhave.pytest_plugin.helpers.bdd import get_scenario


def add_scenario_title_to_report(item: Item) -> None:
    item._obj.__allure_display_name__ = get_scenario(item).name  # type: ignore
