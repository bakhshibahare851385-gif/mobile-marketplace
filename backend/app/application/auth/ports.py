"""Interfaces the authentication application layer depends on."""

from datetime import datetime
from typing import Protocol

from app.application.auth.tokens import TokenClaims, TokenPair
from app.application.auth.users import NewUser, UserRecord
from app.domain.auth.email import Email


class UserRepository(Protocol):
    def create(self, user: NewUser) -> UserRecord: ...

    def find_by_email(self, email: str | Email) -> UserRecord | None: ...

    def get_by_id(self, user_id: str) -> UserRecord | None: ...

    def record_login(self, user_id: str, at: datetime) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, plain_password: str) -> str: ...

    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


class TokenService(Protocol):
    def issue_pair(self, user_id: str, role: str) -> TokenPair: ...

    def decode(self, token: str, expected_type: str) -> TokenClaims: ...

    def rotate_refresh(self, refresh_token: str, role: str | None = None) -> TokenPair: ...
