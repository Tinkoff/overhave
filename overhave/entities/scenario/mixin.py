class PrefixMixin:
    """ Mixin for getting specified data in format of `pytest-bdd` prefix. """

    @staticmethod
    def _as_prefix(key: str) -> str:
        if ":" not in key:
            return f"{key.title()}:"
        return key
