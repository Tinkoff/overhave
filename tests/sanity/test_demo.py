from typing import Callable, List
from unittest import mock

from demo.demo import _run_demo_admin
from overhave.factory import ProxyFactory


class TestOverhaveDemo:
    """ Sanity tests for application demo mode. """

    def test_demo_admin(
        self,
        test_feature_types: List[str],
        flask_run_mock: mock.MagicMock,
        clean_proxy_factory: Callable[[], ProxyFactory],
    ):
        factory = clean_proxy_factory()

        flask_run_mock.assert_not_called()
        assert not factory._factory.has_context
        assert not factory.pytest_patched

        _run_demo_admin()
        flask_run_mock.assert_called_once_with(host="0.0.0.0", port=8076, debug=True)
        assert factory._factory.has_context
        assert factory.pytest_patched
        assert set(factory.feature_extractor.feature_types) == set(test_feature_types)

        # TODO: check steps content
        assert factory.injector.get_steps(test_feature_types[0])
        assert factory.injector.get_steps(test_feature_types[1])
        assert factory.injector.get_steps(test_feature_types[2])

        for feature_type in test_feature_types:
            assert set(factory.plugin_resolver.get_plugins(feature_type)) == {
                f"demo.steps.{feature_type}.given_steps",
                f"demo.steps.{feature_type}.when_steps",
                f"demo.steps.{feature_type}.then_steps",
                "demo.steps.parser",
            }
