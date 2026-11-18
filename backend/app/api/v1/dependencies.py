"""FastAPI dependency wiring for authentication endpoints."""

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.application.auth.errors import InvalidTokenError, UnauthorizedError
from app.application.auth.ports import PasswordHasher, TokenService, UserRepository
from app.application.auth.services import LoginService, RefreshService, RegistrationService
from app.application.auth.users import CurrentUser
from app.core.config import JWT_SECRET_KEY
from app.infrastructure.auth.password_hasher import Argon2idPasswordHasher
from app.infrastructure.auth.token_service import JwtTokenService
from app.infrastructure.db.database import get_session
from app.infrastructure.db.repositories.user import SqliteUserRepository

# Shared so consumed refresh-token IDs survive across requests (MVP in-memory denylist).
_token_service = JwtTokenService(secret=JWT_SECRET_KEY)


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return SqliteUserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return Argon2idPasswordHasher()


def get_token_service() -> TokenService:
    return _token_service


def get_registration_service(
    users: UserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegistrationService:
    return RegistrationService(users, hasher)


def get_login_service(
    users: UserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher),
    tokens: TokenService = Depends(get_token_service),
) -> LoginService:
    return LoginService(users, hasher, tokens)


def get_refresh_service(
    tokens: TokenService = Depends(get_token_service),
) -> RefreshService:
    return RefreshService(tokens)


def get_current_user(
    authorization: str | None = Header(default=None),
    users: UserRepository = Depends(get_user_repository),
    tokens: TokenService = Depends(get_token_service),
) -> CurrentUser:
    """Resolve the bearer access token into the current user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Not authenticated")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = tokens.decode(token, "access")
    except InvalidTokenError as exc:
        raise UnauthorizedError("Not authenticated") from exc

    user = users.get_by_id(claims.subject)
    if user is None or not user.is_active:
        raise UnauthorizedError("Not authenticated")
    return CurrentUser(id=user.id, email=user.email, role=user.role)


__all__ = [
    "get_current_user",
    "get_login_service",
    "get_refresh_service",
    "get_registration_service",
]
