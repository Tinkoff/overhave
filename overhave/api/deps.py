from functools import cache

from overhave.storage import ITestUserStorage, TestUserStorage


@cache
def get_test_user_storage() -> ITestUserStorage:
    return TestUserStorage()
