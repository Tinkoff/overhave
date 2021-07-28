import pytest
from pydantic import ValidationError


class TestTokenizerClient:
    """ Tests for :class:`TokenizerClient`. """

    @pytest.mark.parametrize(("initiator", "vault_server_name"), [("kek", None), (None, "lol"), (None, None)])
    def test_tokenizer_settings_validation(self, test_tokenizer_client_settings_factory) -> None:
        with pytest.raises(ValidationError):
            test_tokenizer_client_settings_factory()
