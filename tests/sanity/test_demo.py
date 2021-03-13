from typing import List
from unittest import mock

from overhave.factory import ProxyFactory


class TestOverhaveDemo:
    """ Sanity tests for application demo mode. """

    def test_clean_factory(
        self, flask_run_mock: mock.MagicMock, test_proxy_factory: ProxyFactory,
    ):
        flask_run_mock.assert_not_called()
        assert not test_proxy_factory._factory.has_context
        assert not test_proxy_factory.pytest_patched

    def test_factory_resolved(
        self, flask_run_mock: mock.MagicMock, test_resolved_factory: ProxyFactory,
    ):
        flask_run_mock.assert_called_once_with(host="0.0.0.0", port=8076, debug=True)
        assert test_resolved_factory._factory.has_context
        assert test_resolved_factory.pytest_patched

    def test_extractor_collect_feature_types(
        self, test_feature_types: List[str], test_resolved_factory: ProxyFactory,
    ):
        assert set(test_resolved_factory.feature_extractor.feature_types) == set(test_feature_types)

    def test_injector_collect_steps(
        self, test_feature_types: List[str], test_resolved_factory: ProxyFactory,
    ):
        # TODO: check steps content
        for feature_type in test_feature_types:
            assert test_resolved_factory.injector.get_steps(feature_type)

    def test_plugin_resolver_collect_plugins(
        self, test_feature_types: List[str], test_resolved_factory: ProxyFactory,
    ):
        for feature_type in test_feature_types:
            assert set(test_resolved_factory.plugin_resolver.get_plugins(feature_type)) == {
                f"demo.steps.{feature_type}.given_steps",
                f"demo.steps.{feature_type}.when_steps",
                f"demo.steps.{feature_type}.then_steps",
                "demo.steps.parser",
            }
