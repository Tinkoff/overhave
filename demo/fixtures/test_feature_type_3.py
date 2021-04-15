from pytest_bdd import scenarios

from overhave import overhave_proxy_manager

FEATURE_TYPE = "feature_type_3"
pytest_plugins = overhave_proxy_manager().plugin_resolver.get_plugins(FEATURE_TYPE)

scenarios(FEATURE_TYPE)
