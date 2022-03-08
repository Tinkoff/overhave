from overhave.storage import ITestUserStorage, TestUserStorage


def get_test_user_storage() -> ITestUserStorage:
    return TestUserStorage()
