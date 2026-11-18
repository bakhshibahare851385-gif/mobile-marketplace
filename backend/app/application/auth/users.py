"""User data transfer objects exchanged with persistence."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.auth.email import Email
from app.domain.auth.role import RegistrationRole


@dataclass(frozen=True)
class NewUser:
    """Everything needed to persist a newly registered account."""

    email: Email
    password_hash: str
    role: RegistrationRole


@dataclass(frozen=True)
class CurrentUser:
    """The authenticated identity attached to a request."""

    id: str
    email: str
    role: str


@dataclass(frozen=True)
class UserRecord:
    """A user as read back from the repository (never an ORM object)."""

    id: str
    email: str
    password_hash: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
