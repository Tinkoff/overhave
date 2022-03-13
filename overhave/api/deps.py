from functools import cache

from overhave.storage import FeatureTagStorage, IFeatureTagStorage, ITestUserStorage, TestUserStorage


@cache
def get_test_user_storage() -> ITestUserStorage:
    return TestUserStorage()


@cache
def get_feature_tag_storage() -> IFeatureTagStorage:
    return FeatureTagStorage()
