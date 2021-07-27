import enum

import gitlab


class InvalidTokenTypeError(Exception):
    """ Error for choosing invalid token type value. """

    pass


class TokenType(enum.Enum):
    """ Enum for token types you want. """

    OAUTH = "oauth"
    PRIVATE = "private"
    JOB = "job"


def get_gl(url: str, token_type: TokenType, token: str) -> gitlab.Gitlab:
    if token_type is TokenType.OAUTH:
        return gitlab.Gitlab(url, oauth_token=token)
    if token_type is TokenType.PRIVATE:
        return gitlab.Gitlab(url, private_token=token)
    if token_type is TokenType.JOB:
        return gitlab.Gitlab(url, private_token=token)
    raise InvalidTokenTypeError(
        f"Please, verify your token type! {token_type} not in {[TokenType.OAUTH, TokenType.JOB, TokenType.PRIVATE]}"
    )
