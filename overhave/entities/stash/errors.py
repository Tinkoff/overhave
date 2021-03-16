class BaseStashManagerException(Exception):
    """ Base exception for :class:`StashManager`. """


class StashPrCreationError(BaseStashManagerException):
    """ Exception for pull-request creation error. """


class NotSpecifiedFeatureTypeError(BaseStashManagerException):
    """ Exception for incorrect feature type error. """
