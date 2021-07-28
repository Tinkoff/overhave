from faker import Faker

from overhave.publication.gitlab.tokenizer.client import TokenizerClient


class TestTokenizerClient:
    """ Tests for :class:`TokenizerClient`. """

    def test_get_token_if_vault_server_name_is_none(self, test_tokenizer_client: TokenizerClient, faker: Faker) -> None:
        token = test_tokenizer_client.get_token(initiator=faker.word(), draft_id=faker.random_int())
        assert token.token is None
