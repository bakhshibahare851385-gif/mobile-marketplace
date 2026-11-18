"""JWT access/refresh token issuance, verification, and rotation."""

from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

import jwt

from app.application.auth.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    UnexpectedTokenTypeError,
)
from app.application.auth.tokens import TokenClaims, TokenPair
from app.domain.auth.token_policy import (
    ACCESS_TOKEN_TTL_SECONDS,
    REFRESH_TOKEN_TTL_SECONDS,
)

Clock = Callable[[], datetime]

_ALLOWED_TYPES = frozenset({"access", "refresh"})
_REQUIRED_CLAIMS = ["sub", "type", "iat", "exp", "jti"]


class JwtTokenService:
    """Issue and verify HS256 JWTs with an injectable clock.

    Refresh rotation consumes the old token's ``jti`` in an in-memory set. This
    is deliberately process-local for the MVP; a shared denylist replaces it at
    scale (see ADR-0010 and the auth SPEC).
    """

    def __init__(self, secret: str, clock: Clock | None = None) -> None:
        if not secret:
            raise ValueError("JWT secret must not be empty")
        self._secret = secret
        self._clock: Clock = clock or (lambda: datetime.now(timezone.utc))
        self._consumed_refresh_jtis: set[str] = set()

    # -- issuance ---------------------------------------------------------

    def issue_access(self, user_id: str, role: str) -> str:
        return self._encode(user_id, role, "access", ACCESS_TOKEN_TTL_SECONDS)

    def issue_refresh(self, user_id: str, role: str | None = None) -> str:
        return self._encode(user_id, role, "refresh", REFRESH_TOKEN_TTL_SECONDS)

    def issue_pair(self, user_id: str, role: str) -> TokenPair:
        return TokenPair(
            access_token=self.issue_access(user_id, role),
            refresh_token=self.issue_refresh(user_id, role),
            expires_in=ACCESS_TOKEN_TTL_SECONDS,
            refresh_expires_in=REFRESH_TOKEN_TTL_SECONDS,
        )

    def _encode(
        self, user_id: str, role: str | None, token_type: str, ttl_seconds: int
    ) -> str:
        issued_at = int(self._clock().timestamp())
        payload: dict[str, object] = {
            "sub": user_id,
            "type": token_type,
            "iat": issued_at,
            "exp": issued_at + ttl_seconds,
            "jti": str(uuid4()),
            # Carried internally so rotation can mint a new access token without
            # a database lookup. Public decode() hides it on refresh tokens.
            "role": role,
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    # -- decoding ---------------------------------------------------------

    def decode(self, token: str, expected_type: str) -> TokenClaims:
        payload = self._decode_payload(token, expected_type)
        return TokenClaims(
            subject=payload["sub"],
            role=payload.get("role") if payload["type"] == "access" else None,
            token_type=payload["type"],
            issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            jti=payload["jti"],
        )

    def _decode_payload(self, token: str, expected_type: str) -> dict:
        if not isinstance(token, str) or not token:
            raise InvalidTokenError("Token must be a non-empty string")
        if expected_type not in _ALLOWED_TYPES:
            raise UnexpectedTokenTypeError(
                f"Unsupported expected token type: {expected_type!r}"
            )

        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                options={
                    "verify_exp": False,  # expiry is checked against the injected clock
                    "verify_iat": False,
                    "require": _REQUIRED_CLAIMS,
                },
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("Token is invalid") from exc

        token_type = payload.get("type")
        if token_type not in _ALLOWED_TYPES:
            raise InvalidTokenError("Token has an invalid type claim")
        if token_type != expected_type:
            raise UnexpectedTokenTypeError(
                f"Expected a {expected_type} token, got {token_type}"
            )

        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if self._clock() >= expires_at:
            raise ExpiredTokenError("Token has expired")

        return payload

    # -- rotation ---------------------------------------------------------

    def rotate_refresh(
        self, refresh_token: str, role: str | None = None
    ) -> TokenPair:
        payload = self._decode_payload(refresh_token, "refresh")
        jti = payload["jti"]
        if jti in self._consumed_refresh_jtis:
            raise InvalidTokenError("Refresh token has already been rotated")
        self._consumed_refresh_jtis.add(jti)

        new_role = role if role is not None else payload.get("role")
        return self.issue_pair(payload["sub"], new_role)
