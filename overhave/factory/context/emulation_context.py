from typing import Optional

from overhave.entities import OverhaveEmulationSettings
from overhave.factory.context.base_context import BaseFactoryContext


class OverhaveEmulationContext(BaseFactoryContext):
    """Overhave emulation context, based on application BaseSettings.

    This context defines how Overhave emulation will work.
    """

    def __init__(self, emulation_settings: Optional[OverhaveEmulationSettings] = None) -> None:
        super().__init__(emulation_settings=emulation_settings or OverhaveEmulationSettings())
