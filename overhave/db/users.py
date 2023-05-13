import enum

import sqlalchemy as sa
import sqlalchemy_utils as su

from overhave.db.base import BaseTable, PrimaryKeyMixin


class Role(enum.StrEnum):
    """Enum that declares user access roles."""

    user = "user"
    admin = "admin"


@su.generic_repr("login", "role")
class UserRole(BaseTable, PrimaryKeyMixin):
    """User access table."""

    login: str = sa.Column(sa.String(), nullable=False, unique=True)
    password: str | None = sa.Column(sa.String())
    role: Role = sa.Column(sa.Enum(Role), nullable=False, default=Role.user)

    def __repr__(self) -> str:
        return f"{self.login} ({self.role})"


@su.generic_repr("group")
class GroupRole(BaseTable, PrimaryKeyMixin):
    """Group access table."""

    group: str = sa.Column(sa.String(), nullable=False, unique=True)
