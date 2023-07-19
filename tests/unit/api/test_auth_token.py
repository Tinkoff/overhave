import pytest

from overhave.api.auth import AuthTokenData
from overhave.api.auth.token import get_token_data
from overhave.api.settings import OverhaveApiAuthSettings


@pytest.fixture()
def auth_settings() -> OverhaveApiAuthSettings:
    return OverhaveApiAuthSettings(secret_key="secret")


class TestAuthToken:
    """Tests for get jwt-token payload."""

    @pytest.mark.parametrize(
        ("token", "expected_value"),
        [
            (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdHViIjoicXdlcnR5In0."
                "jsJEgGO9F0h2A-DuJqFxT2XhfZ_I-pK1bZPWP76ZczQ",
                None,
            ),
            (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJxd2VydHkifQ."
                "6G7k5vyAcQPCMGmIhHH-dH1eHltTuhRg6o-cy6QdCnk",
                AuthTokenData(username="qwerty"),
            ),
        ],
    )
    def test_get_token_data(
        self,
        auth_settings: OverhaveApiAuthSettings,
        token: str,
        expected_value: AuthTokenData | None,
    ) -> None:
        assert get_token_data(auth_settings, token) == expected_value
