import enum


class OverhaveS3Bucket(str, enum.Enum):
    """ Declared Overhave service buckets names for s3 usage. """

    REPORTS = "overhave_reports"
    EXTRA = "overhave_extra"
