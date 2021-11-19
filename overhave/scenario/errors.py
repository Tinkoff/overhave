class ScenarioCompilerError(Exception):
    """Base exception for :class:`ScenarioCompiler` errors."""


class IncorrectScenarioTextError(ScenarioCompilerError):
    """Exception for incorrect scenario text format."""


class ScenarioParserError(Exception):
    """Base exception for parsing error."""


class FeatureNameParsingError(ScenarioParserError):
    """Exception for feature name parsing error."""


class FeatureTypeParsingError(ScenarioParserError):
    """Exception for feature type parsing error."""


class AdditionalInfoParsingError(ScenarioParserError):
    """Exception for additional info parsing error."""


class DatetimeParsingError(ScenarioParserError):
    """Exception for datetime parsing error."""
