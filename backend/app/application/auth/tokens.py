"""Token value objects returned by the token service."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenClaims:
    """Verified claims of a decoded token."""

    subject: str
    role: str | None
    token_type: str
    issued_at: datetime
    expires_at: datetime
    jti: str


@dataclass(frozen=True)
class TokenPair:
    """An access token and its rotating refresh token."""

    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
