import pytest

from overhave.transport.http.gitlab_client.utils import InvalidTokenTypeError


class TestGitlabPythonClient:
    """ Unit tests for gitlab-python utils. """

    @pytest.mark.parametrize(("token_type", "token"), [("gotcha", "peka")])
    def test_get_gitlab_python_client_raises_error(self, test_gitlab_python_client_factory) -> None:
        with pytest.raises(InvalidTokenTypeError):
            test_gitlab_python_client_factory()
