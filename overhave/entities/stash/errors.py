class StashValidationError(ValueError):
    """ Exception for stash response validation error. """


class StashPrCreationError(RuntimeError):
    """ Exception for pull-request creation error. """


class NotSpecifiedFeatureTypeError(RuntimeError):
    """ Exception for incorrect feature type error. """
