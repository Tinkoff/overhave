import enum
from typing import Optional

import sqlalchemy as sa
import sqlalchemy_utils as su

from overhave.db.base import BaseTable, PrimaryKeyMixin


class Role(str, enum.Enum):
    """Enum that declares user access roles."""

    user = "user"
    admin = "admin"


@su.generic_repr("login", "role")
class UserRole(BaseTable, PrimaryKeyMixin):
    """User access table."""

    login = sa.Column(sa.String(), nullable=False, unique=True)
    password = sa.Column(sa.String(), nullable=True)
    role = sa.Column(sa.Enum(Role), nullable=False, default=Role.user)

    def __init__(self, login: str, password: Optional[str], role: Role) -> None:
        self.login = login
        self.password = password
        self.role = role

    def __repr__(self) -> str:
        return f"{self.login} ({self.role})"


@su.generic_repr("group")
class GroupRole(BaseTable, PrimaryKeyMixin):
    """Group access table."""

    group = sa.Column(sa.String(), nullable=False, unique=True)

    def __init__(self, group: str) -> None:
        self.group = group
