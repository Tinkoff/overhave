from typing import Optional

from overhave.entities import OverhaveEmulationSettings


class OverhaveEmulationContext:
    """ Overhave emulation context, based on application BaseSettings.

    This context defines how Overhave emulation will work.
    """

    def __init__(self, emulation_settings: Optional[OverhaveEmulationSettings] = None) -> None:
        self.emulation_settings = emulation_settings or OverhaveEmulationSettings()
