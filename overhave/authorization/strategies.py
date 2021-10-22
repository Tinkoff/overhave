import enum


class AuthorizationStrategy(str, enum.Enum):
    """
    Authorization strategies Enum.

    Simple - strategy without real authorization. Each user could use preferred name. This name will be used for user
    authority. Each user is unique. Password not required.
    Default - strategy with real authorization. Each user could use only registered credentials.
    LDAP - strategy with authorization using remote LDAP server. Each user should use his LDAP credentials. LDAP
    server returns user groups. If user in default 'admin' group or his groups list contains admin group - user
    will be authorized. If user already placed in database - user will be authorized too. No one password stores.
    """

    SIMPLE = "simple"
    DEFAULT = "default"
    LDAP = "ldap"
