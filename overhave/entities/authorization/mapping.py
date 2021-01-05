from typing import Mapping, Type

from overhave.entities.authorization.manager import (
    DefaultAdminAuthorizationManager,
    IAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    SimpleAdminAuthorizationManager,
)
from overhave.entities.authorization.strategies import AuthorizationStrategy

AUTH_STRATEGY_TO_MANAGER_MAPPING: Mapping[AuthorizationStrategy, Type[IAdminAuthorizationManager]] = {
    AuthorizationStrategy.SIMPLE: SimpleAdminAuthorizationManager,
    AuthorizationStrategy.DEFAULT: DefaultAdminAuthorizationManager,
    AuthorizationStrategy.LDAP: LDAPAdminAuthorizationManager,
}
