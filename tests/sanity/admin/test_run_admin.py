from typing import List, Tuple, cast
from unittest import mock

import pytest

from demo.settings import OverhaveDemoAppLanguage
from overhave import db
from overhave.entities import FeatureTypeModel, FeatureTypeName
from overhave.factory import AdminFactory
from overhave.pytest_plugin import IProxyManager


class TestOverhaveRunAdminClean:
    """ Sanity tests for application admin mode. """

    def test_clean_factory(
        self, flask_run_mock: mock.MagicMock, test_admin_factory: AdminFactory, test_proxy_manager: IProxyManager,
    ) -> None:
        flask_run_mock.assert_not_called()
        assert not test_admin_factory._context
        assert not test_proxy_manager.pytest_patched


@pytest.mark.parametrize("test_demo_language", list(OverhaveDemoAppLanguage), indirect=True)
class TestOverhaveRunAdmin:
    """ Sanity tests for application admin mode. """

    def test_factory_resolved(
        self, flask_run_mock: mock.MagicMock, test_resolved_admin_proxy_manager: IProxyManager,
    ) -> None:
        flask_run_mock.assert_called_once_with(host="localhost", port=8076, debug=True)
        assert cast(AdminFactory, test_resolved_admin_proxy_manager.factory)._context
        assert test_resolved_admin_proxy_manager.pytest_patched

    def test_extractor_collect_feature_types(
        self, test_feature_types: Tuple[str, ...], test_resolved_admin_proxy_manager: IProxyManager,
    ) -> None:
        assert set(test_resolved_admin_proxy_manager.factory.feature_extractor.feature_types) == set(test_feature_types)

    def test_db_feature_types_exists(
        self, test_feature_types: Tuple[str, ...], test_resolved_admin_proxy_manager: IProxyManager,
    ) -> None:
        feature_type_models: List[FeatureTypeModel] = []
        with db.create_session() as session:
            db_feature_types = session.query(db.FeatureType).all()
            feature_type_models.extend([FeatureTypeModel.from_orm(feature_type) for feature_type in db_feature_types])
        assert len(feature_type_models) == len(test_feature_types)
        assert {model.name for model in feature_type_models} == set(test_feature_types)

    def test_plugin_resolver_collect_plugins(
        self, test_feature_types: Tuple[str, ...], test_resolved_admin_proxy_manager: IProxyManager,
    ) -> None:
        for feature_type in test_feature_types:
            assert set(test_resolved_admin_proxy_manager.plugin_resolver.get_plugins(feature_type)) == {
                f"demo.steps.{feature_type}.given_steps",
                f"demo.steps.{feature_type}.when_steps",
                f"demo.steps.{feature_type}.then_steps",
                "demo.steps.parser",
            }

    def test_injector_collect_steps(
        self, test_feature_types: Tuple[str, ...], test_resolved_admin_proxy_manager: IProxyManager,
    ) -> None:
        # TODO: check steps content
        for feature_type in test_feature_types:
            assert test_resolved_admin_proxy_manager.factory.step_collector.get_steps(FeatureTypeName(feature_type))
