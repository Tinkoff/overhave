from overhave.base_settings import BaseOverhavePrefix


class OverhaveScenarioCompilerSettings(BaseOverhavePrefix):
    """Settings for scenario compiling and parsing."""

    tag_prefix: str = "@"
    id_prefix: str = "ID:"
    created_by_prefix: str = "# created by"
    last_edited_by_prefix: str = "last edited by"
    published_by_prefix: str = "published by"
    severity_prefix: str = "@severity."

    time_delimiter: str = ","
    time_format: str = "%d-%m-%Y %H:%M:%S"
    blocks_delimiter: str = "|"

    @property
    def severity_keyword(self) -> str:
        return self.severity_prefix.removeprefix(self.tag_prefix)
