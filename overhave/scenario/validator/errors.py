class BaseFeatureValidatorException(Exception):
    """Base exception for :class:`FeatureValidator`."""


class FeaturesWithoutIDPresenceError(BaseFeatureValidatorException):
    """Exception for situation with nullable ID features presence."""


class IncorrectFeaturesPresenceError(BaseFeatureValidatorException):
    """Exception for situation with incorrect features presence."""


class DuplicateFeatureIDError(BaseFeatureValidatorException):
    """Exception for situation with duplicate feature IDs."""
