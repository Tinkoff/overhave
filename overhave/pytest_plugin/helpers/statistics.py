from typing import cast

from _pytest.nodes import Item
from _pytest.reports import TestReport


def set_item_call_report(item: Item, report: TestReport) -> None:
    setattr(item, "call_report", report)


def get_item_call_report(item: Item) -> TestReport:
    return cast(TestReport, getattr(item, "call_report"))
