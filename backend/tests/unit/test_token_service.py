"""RED phase tests for JWT access/refresh token service (PLAN Step 2).

Expected to FAIL at collection: ``app.infrastructure.auth.token_service`` and
``app.application.auth.errors`` do not exist yet.

Contract (docs/features/auth/SPEC.md, FR-AUTH-6/7/13/14):
  - access JWT: sub, role, iat, exp, jti, type="access"; TTL 1800s
  - refresh JWT: sub, iat, exp, jti, type="refresh"; TTL 604800s
  - decode verifies signature, expiry, and expected token type
  - refresh rotation issues a new pair and consumes the old refresh token jti
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.application.auth.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    UnexpectedTokenTypeError,
)
from app.domain.auth.token_policy import (
    ACCESS_TOKEN_TTL_SECONDS,
    REFRESH_TOKEN_TTL_SECONDS,
)
from app.infrastructure.auth.token_service import JwtTokenService

SECRET = "test-secret-key-with-at-least-32-characters"
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FixedClock:
    """Injectable clock so expiry tests never depend on wall time."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: int) -> None:
        self.now += timedelta(seconds=seconds)


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(NOW)


@pytest.fixture
def service(clock: FixedClock) -> JwtTokenService:
    return JwtTokenService(secret=SECRET, clock=clock)


# ---------------------------------------------------------------------------
# Issuance and claims
# ---------------------------------------------------------------------------


def test_issue_access_token_has_required_claims(service):
    token = service.issue_access(user_id="user-123", role="buyer")
    claims = service.decode(token, expected_type="access")

    assert claims.subject == "user-123"
    assert claims.role == "buyer"
    assert claims.token_type == "access"
    assert claims.issued_at == NOW
    assert claims.expires_at == NOW + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)
    assert claims.jti  # non-empty unique token id


def test_issue_refresh_token_has_required_claims(service):
    token = service.issue_refresh(user_id="user-123")
    claims = service.decode(token, expected_type="refresh")

    assert claims.subject == "user-123"
    assert claims.role is None
    assert claims.token_type == "refresh"
    assert claims.issued_at == NOW
    assert claims.expires_at == NOW + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS)
    assert claims.jti


def test_two_access_tokens_have_distinct_jtis(service):
    first = service.decode(service.issue_access("user-123", "buyer"), "access")
    second = service.decode(service.issue_access("user-123", "buyer"), "access")

    assert first.jti != second.jti


def test_issue_pair_returns_both_tokens_and_ttls(service):
    pair = service.issue_pair(user_id="user-123", role="seller")

    assert service.decode(pair.access_token, "access").subject == "user-123"
    assert service.decode(pair.refresh_token, "refresh").subject == "user-123"
    assert pair.expires_in == ACCESS_TOKEN_TTL_SECONDS
    assert pair.refresh_expires_in == REFRESH_TOKEN_TTL_SECONDS


# ---------------------------------------------------------------------------
# Signature, tampering, and malformed input
# ---------------------------------------------------------------------------


def test_decode_rejects_token_signed_with_another_secret(clock):
    other = JwtTokenService(secret="a-completely-different-secret-value", clock=clock)
    token = other.issue_access("user-123", "buyer")

    with pytest.raises(InvalidTokenError):
        JwtTokenService(secret=SECRET, clock=clock).decode(token, "access")


def test_decode_rejects_tampered_token(service):
    token = service.issue_access("user-123", "buyer")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(InvalidTokenError):
        service.decode(tampered, "access")


@pytest.mark.parametrize("garbage", ["", "not-a-jwt", "a.b.c", None])
def test_decode_rejects_garbage_token(service, garbage):
    with pytest.raises(InvalidTokenError):
        service.decode(garbage, "access")


# ---------------------------------------------------------------------------
# Expiry
# ---------------------------------------------------------------------------


def test_access_token_is_valid_until_ttl(service, clock):
    token = service.issue_access("user-123", "buyer")

    clock.advance(ACCESS_TOKEN_TTL_SECONDS - 1)
    assert service.decode(token, "access").subject == "user-123"

    clock.advance(1)
    with pytest.raises(ExpiredTokenError):
        service.decode(token, "access")


def test_refresh_token_is_valid_until_ttl(service, clock):
    token = service.issue_refresh("user-123")

    clock.advance(REFRESH_TOKEN_TTL_SECONDS - 1)
    assert service.decode(token, "refresh").subject == "user-123"

    clock.advance(1)
    with pytest.raises(ExpiredTokenError):
        service.decode(token, "refresh")


def test_expired_token_error_is_an_invalid_token_error():
    assert issubclass(ExpiredTokenError, InvalidTokenError)
    assert issubclass(UnexpectedTokenTypeError, InvalidTokenError)


# ---------------------------------------------------------------------------
# Token type separation (FR-AUTH-14)
# ---------------------------------------------------------------------------


def test_refresh_token_cannot_be_used_as_access_token(service):
    refresh = service.issue_refresh("user-123")

    with pytest.raises(UnexpectedTokenTypeError):
        service.decode(refresh, "access")


def test_access_token_cannot_be_used_as_refresh_token(service):
    access = service.issue_access("user-123", "buyer")

    with pytest.raises(UnexpectedTokenTypeError):
        service.decode(access, "refresh")


def test_decode_rejects_unknown_expected_type(service):
    access = service.issue_access("user-123", "buyer")

    with pytest.raises(UnexpectedTokenTypeError):
        service.decode(access, "admin")


# ---------------------------------------------------------------------------
# Refresh rotation (FR-AUTH-13 / AC-10)
# ---------------------------------------------------------------------------


def test_rotate_refresh_returns_new_access_and_refresh_tokens(service):
    pair = service.issue_pair("user-123", "seller")

    rotated = service.rotate_refresh(pair.refresh_token)

    assert rotated.access_token != pair.access_token
    assert rotated.refresh_token != pair.refresh_token
    assert service.decode(rotated.access_token, "access").role == "seller"
    assert service.decode(rotated.refresh_token, "refresh").subject == "user-123"


def test_old_refresh_token_cannot_be_rotated_twice(service):
    pair = service.issue_pair("user-123", "seller")
    service.rotate_refresh(pair.refresh_token)

    with pytest.raises(InvalidTokenError):
        service.rotate_refresh(pair.refresh_token)


def test_rotated_refresh_token_can_be_rotated_again(service):
    first = service.issue_pair("user-123", "seller")
    second = service.rotate_refresh(first.refresh_token)
    third = service.rotate_refresh(second.refresh_token)

    assert service.decode(third.refresh_token, "refresh").subject == "user-123"


def test_rotate_refresh_rejects_expired_token(service, clock):
    pair = service.issue_pair("user-123", "seller")
    clock.advance(REFRESH_TOKEN_TTL_SECONDS)

    with pytest.raises(ExpiredTokenError):
        service.rotate_refresh(pair.refresh_token)


def test_rotate_refresh_rejects_access_token(service):
    access = service.issue_access("user-123", "buyer")

    with pytest.raises(UnexpectedTokenTypeError):
        service.rotate_refresh(access)
