from typing import Callable
from unittest import mock

from demo.demo import _run_demo_admin
from overhave.factory import ProxyFactory


class TestOverhaveDemo:
    """ Sanity tests for application demo mode. """

    def test_demo_admin(self, flask_run_mock: mock.MagicMock, clean_proxy_factory: Callable[[], ProxyFactory]):
        factory = clean_proxy_factory()

        flask_run_mock.assert_not_called()
        assert not factory._factory.has_context
        assert not factory.pytest_patched

        _run_demo_admin()
        flask_run_mock.assert_called_once_with(host="0.0.0.0", port=8076, debug=True)
        assert factory._factory.has_context
        assert factory.pytest_patched
        assert set(factory.feature_extractor.feature_types) == {"feature_type_1", "feature_type_2", "feature_type_3"}

        # TODO: check steps content
        assert factory.injector.get_steps("feature_type_1")
        assert factory.injector.get_steps("feature_type_2")
        assert factory.injector.get_steps("feature_type_3")
