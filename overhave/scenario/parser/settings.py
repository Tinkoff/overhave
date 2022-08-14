from overhave.base_settings import BaseOverhavePrefix


class OverhaveScenarioParserSettings(BaseOverhavePrefix):
    """Settings for scenario parser."""

    parser_strict_mode: bool = False  # ScenarioParser mode; if strict - necessary fields will be validated
