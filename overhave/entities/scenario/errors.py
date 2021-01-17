class ScenarioCompilerError(Exception):
    """ Base exception for :class:`ScenarioCompiler` errors. """

    pass


class IncorrectScenarioTextError(ScenarioCompilerError):
    """ Exception for incorrect scenario text format. """

    pass


class ScenarioParserError(Exception):
    """ Base exception for parsing error. """

    pass


class FeatureNameParsingError(ScenarioParserError):
    """ Exception for feature name parsing error. """

    pass


class FeatureTypeParsingError(ScenarioParserError):
    """ Exception for feature type parsing error. """

    pass


class LastEditorParsingError(ScenarioParserError):
    """ Exception for last editor parsing error. """

    pass
