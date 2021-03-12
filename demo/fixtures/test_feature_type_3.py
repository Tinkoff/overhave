from pytest_bdd import scenarios

from overhave import overhave_factory

FEATURE_TYPE = "feature_type_3"
pytest_plugins = overhave_factory().plugin_resolver.get_plugins(FEATURE_TYPE)

scenarios(f"../features_structure_example/{FEATURE_TYPE}")
