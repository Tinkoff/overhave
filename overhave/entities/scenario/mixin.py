class PrefixMixin:
    @staticmethod
    def _as_prefix(key: str) -> str:
        if ":" not in key:
            return f"{key.title()}:"
        return key
