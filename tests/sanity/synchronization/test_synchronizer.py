import pytest

from demo.settings import OverhaveDemoAppLanguage
from overhave.synchronization import OverhaveSynchronizer


@pytest.mark.parametrize("test_demo_language", list(OverhaveDemoAppLanguage), indirect=True)
class TestOverhaveSynchronizer:
    """ Sanity tests for application admin mode. """

    def test_synchronize(self, test_resolved_synchronizer: OverhaveSynchronizer) -> None:
        pass
