"""Authentication application services."""

from datetime import datetime, timezone

from app.application.auth.errors import InvalidCredentialsError
from app.application.auth.ports import PasswordHasher, TokenService, UserRepository
from app.application.auth.tokens import TokenPair
from app.application.auth.users import NewUser, UserRecord
from app.domain.auth.email import Email, InvalidEmailError, normalize_email
from app.domain.auth.password import PasswordPolicy
from app.domain.auth.role import RegistrationRole, parse_registration_role


class RegistrationService:
    """Register a new buyer or seller account."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher

    def register(self, email: str, password: str, role: str) -> UserRecord:
        PasswordPolicy.validate(password)
        normalized_email = normalize_email(email)
        registration_role = parse_registration_role(role)
        password_hash = self._hasher.hash(password)
        return self._users.create(
            NewUser(
                email=Email(normalized_email),
                password_hash=password_hash,
                role=registration_role,
            )
        )


class LoginService:
    """Verify credentials and issue an access/refresh token pair."""

    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def login(self, email: str, password: str) -> tuple[UserRecord, TokenPair]:
        try:
            user = self._users.find_by_email(email)
        except InvalidEmailError:
            user = None

        if user is None or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        self._users.record_login(user.id, datetime.now(timezone.utc))
        return user, self._tokens.issue_pair(user.id, user.role)


class RefreshService:
    """Rotate a refresh token into a fresh access/refresh pair."""

    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def refresh(self, refresh_token: str) -> TokenPair:
        return self._tokens.rotate_refresh(refresh_token)
