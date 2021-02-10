from typing import List

import allure
from markupsafe import Markup

from overhave.testing.settings import OverhaveDescriptionManagerSettings


class DescriptionManager:
    """ Class for test-suit custom description management and setting to Allure report. """

    def __init__(self, settings: OverhaveDescriptionManagerSettings):
        self._settings = settings

        self._description: List[str] = []

    def apply_description(self) -> None:
        if self._description:
            joined_description = self._settings.blocks_delimiter.join(self._description)
            allure.dynamic.description_html(Markup(joined_description))

    def add_description(self, value: str) -> None:
        self._description.append(value)

    def add_description_above(self, value: str) -> None:
        self._description.insert(0, value)
