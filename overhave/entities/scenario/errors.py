class ScenarioCompilerError(Exception):
    pass


class IncorrectScenarioTextError(ScenarioCompilerError):
    pass


class ScenarioParserError(Exception):
    pass


class FeatureNameParsingError(ScenarioParserError):
    pass


class FeatureTypeParsingError(ScenarioParserError):
    pass


class LastEditorParsingError(ScenarioParserError):
    pass
