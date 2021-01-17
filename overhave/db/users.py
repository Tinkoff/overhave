import enum
from typing import TYPE_CHECKING, Optional, cast

import sqlalchemy as sa
import sqlalchemy_utils as su

from overhave.db.base import Base, PrimaryKeyMixin
from overhave.db.types import LONG_STR_TYPE, SHORT_STR_TYPE


class Role(str, enum.Enum):
    """ Enum that declares user access roles. """

    user = 'user'
    admin = 'admin'


class BaseUser:
    """ Base user class. """

    login: str = sa.Column(SHORT_STR_TYPE, nullable=False, unique=True)
    password: Optional[str] = sa.Column(LONG_STR_TYPE, nullable=True)
    role: str = sa.Column(sa.Enum(Role), nullable=False, default=Role.user)

    if TYPE_CHECKING:
        id: int

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.id

    # Required for administrative interface
    def __unicode__(self) -> str:
        return cast(str, self.login)

    def __str__(self) -> str:
        return cast(str, self.login)


@su.generic_repr('login')
class UserRole(Base, PrimaryKeyMixin, BaseUser):
    """ User access table. """

    def __init__(self, login: str, password: Optional[str], role: Role) -> None:
        self.login = login
        self.password = password
        self.role = role


@su.generic_repr('group')
class GroupRole(Base, PrimaryKeyMixin):
    """ Group access table. """

    group = sa.Column(SHORT_STR_TYPE, nullable=False, unique=True)

    def __init__(self, group: str) -> None:
        self.group = group
