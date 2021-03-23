from typing import List
from unittest import mock

from overhave import db
from overhave.entities import FeatureTypeModel


class TestOverhaveRunAdmin:
    """ Sanity tests for application admin mode. """

    def test_clean_factory(
        self, flask_run_mock: mock.MagicMock, test_proxy_manager,
    ):
        flask_run_mock.assert_not_called()
        assert not test_proxy_manager._factory.has_context
        assert not test_proxy_manager.pytest_patched

    def test_factory_resolved(
        self, flask_run_mock: mock.MagicMock, test_resolved_proxy_manager,
    ):
        flask_run_mock.assert_called_once_with(host="0.0.0.0", port=8076, debug=True)
        assert test_resolved_proxy_manager._factory.has_context
        assert test_resolved_proxy_manager.pytest_patched

    def test_extractor_collect_feature_types(
        self, test_feature_types: List[str], test_resolved_proxy_manager,
    ):
        assert set(test_resolved_proxy_manager.feature_extractor.feature_types) == set(test_feature_types)

    def test_db_feature_types_exists(
        self, test_feature_types: List[str], test_resolved_proxy_manager,
    ):
        feature_type_models: List[FeatureTypeModel] = []
        with db.create_session() as session:
            db_feature_types = session.query(db.FeatureType).all()
            feature_type_models.extend([FeatureTypeModel.from_orm(feature_type) for feature_type in db_feature_types])
        assert len(feature_type_models) == len(test_feature_types)
        assert {model.name for model in feature_type_models} == set(test_feature_types)

    def test_injector_collect_steps(
        self, test_feature_types: List[str], test_resolved_proxy_manager,
    ):
        # TODO: check steps content
        for feature_type in test_feature_types:
            assert test_resolved_proxy_manager.injector.get_steps(feature_type)

    def test_plugin_resolver_collect_plugins(
        self, test_feature_types: List[str], test_resolved_proxy_manager,
    ):
        for feature_type in test_feature_types:
            assert set(test_resolved_proxy_manager.plugin_resolver.get_plugins(feature_type)) == {
                f"demo.steps.{feature_type}.given_steps",
                f"demo.steps.{feature_type}.when_steps",
                f"demo.steps.{feature_type}.then_steps",
                "demo.steps.parser",
            }
