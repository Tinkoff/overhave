from typing import Callable

import gitlab
import pytest
from faker import Faker

from overhave.transport.http.gitlab_client.objects import TokenType
from overhave.transport.http.gitlab_client.utils import get_gitlab_python_client


@pytest.fixture()
def test_gitlab_python_client_factory(faker: Faker, token_type: TokenType, token: str) -> Callable[[], gitlab.Gitlab]:
    def test_gitlab_python_client() -> gitlab.Gitlab:
        return get_gitlab_python_client(url=f"http://{faker.word()}.com", token_type=token_type, token=token)

    return test_gitlab_python_client
