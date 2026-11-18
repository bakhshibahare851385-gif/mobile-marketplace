"""SQLite-backed user repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.auth.errors import DuplicateEmailError
from app.application.auth.users import NewUser, UserRecord
from app.domain.auth.email import Email, normalize_email
from app.domain.auth.role import RegistrationRole
from app.infrastructure.db.models.user import User


class SqliteUserRepository:
    """Persist and retrieve users, returning application DTOs only."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, user: NewUser) -> UserRecord:
        row = User(
            email=_email_value(user.email),
            password_hash=user.password_hash,
            role=_role_value(user.role),
        )
        self._session.add(row)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateEmailError(
                "An account with this email already exists"
            ) from exc
        return self._to_record(row)

    def find_by_email(self, email: str | Email) -> UserRecord | None:
        value = normalize_email(email.value if isinstance(email, Email) else email)
        row = self._session.scalar(select(User).where(User.email == value))
        return self._to_record(row) if row is not None else None

    def get_by_id(self, user_id: str) -> UserRecord | None:
        row = self._session.get(User, user_id)
        return self._to_record(row) if row is not None else None

    def record_login(self, user_id: str, at: datetime) -> None:
        row = self._session.get(User, user_id)
        if row is not None:
            row.last_login_at = at
            self._session.commit()

    @staticmethod
    def _to_record(row: User) -> UserRecord:
        return UserRecord(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            role=row.role,
            is_active=row.is_active,
            created_at=row.created_at,
            last_login_at=row.last_login_at,
        )


def _email_value(email: Email | str) -> str:
    return normalize_email(email.value if isinstance(email, Email) else email)


def _role_value(role: RegistrationRole | str) -> str:
    return role.value if isinstance(role, RegistrationRole) else str(role)
