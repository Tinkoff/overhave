from _pytest.nodes import Item
from pytest_bdd.parser import Scenario, Step


def get_scenario(item: Item) -> Scenario:
    return item._obj.__scenario__  # type: ignore


def is_pytest_bdd_item(item: Item) -> bool:
    if hasattr(item, "_obj"):
        return hasattr(item._obj, "__scenario__") and isinstance(get_scenario(item), Scenario)  # type: ignore
    return False


def get_full_step_name(step: Step) -> str:
    return f"{step.keyword} {step._name}"
