"""RED phase tests for the Authentication domain (PLAN Step 1).

These tests describe the required domain behavior before any implementation
exists. They are expected to FAIL at collection with ModuleNotFoundError until
the corresponding modules under ``app/domain/auth/`` are implemented.

Rules under test (docs/features/auth/SPEC.md):
  - email: trimmed + lowercased, basic shape validation, value-object equality
  - password: 8-72 characters inclusive
  - role: only 'buyer' and 'seller' may self-register
  - token policy: access TTL 1800s, refresh TTL 604800s, refresh outlives access,
    expiry boundary behavior
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.domain.auth.email import Email, InvalidEmailError, normalize_email
from app.domain.auth.password import PasswordPolicy, PasswordPolicyError
from app.domain.auth.role import InvalidRoleError, RegistrationRole, parse_registration_role
from app.domain.auth.token_policy import (
    ACCESS_TOKEN_TTL_SECONDS,
    REFRESH_TOKEN_TTL_SECONDS,
    is_expired,
)


# ---------------------------------------------------------------------------
# Email normalization and validation
# ---------------------------------------------------------------------------


def test_normalize_email_trims_surrounding_whitespace():
    assert normalize_email("  buyer@example.com  ") == "buyer@example.com"


def test_normalize_email_lowercases_local_part_and_domain():
    assert normalize_email("Buyer@Example.COM") == "buyer@example.com"


def test_normalize_email_is_idempotent():
    once = normalize_email("  MiXeD@Example.Com ")
    assert normalize_email(once) == once


def test_normalize_email_preserves_plus_tag():
    assert normalize_email("Buyer+Tag@Example.com") == "buyer+tag@example.com"


@pytest.mark.parametrize(
    "raw_email",
    [
        "",
        "   ",
        "plainaddress",
        "missing@",
        "@no-local.com",
        "double@@example.com",
        "no-dot@example",
        None,
    ],
)
def test_normalize_email_rejects_invalid_addresses(raw_email):
    with pytest.raises(InvalidEmailError):
        normalize_email(raw_email)


def test_email_value_object_normalizes_on_construction():
    email = Email("  Buyer@Example.COM  ")
    assert email.value == "buyer@example.com"


def test_email_value_object_equality_uses_normalized_value():
    assert Email("Buyer@Example.com") == Email(" buyer@example.com ")
    assert Email("buyer@example.com") != Email("seller@example.com")


def test_email_value_object_rejects_invalid_address():
    with pytest.raises(InvalidEmailError):
        Email("not-an-email")


def test_email_value_object_repr_does_not_leak_unexpected_format():
    assert repr(Email("buyer@example.com")) == "Email('buyer@example.com')"


# ---------------------------------------------------------------------------
# Password policy
# ---------------------------------------------------------------------------


def test_password_policy_constants_match_spec():
    assert PasswordPolicy.MIN_LENGTH == 8
    assert PasswordPolicy.MAX_LENGTH == 72


@pytest.mark.parametrize(
    "password",
    [
        "12345678",  # exactly the minimum
        "s3curePass!",
        "x" * 72,  # exactly the maximum
    ],
)
def test_password_policy_accepts_valid_lengths(password):
    assert PasswordPolicy.validate(password) is None


@pytest.mark.parametrize(
    "password",
    [
        "",
        "short",  # 5 characters
        "x" * 7,  # one below the minimum
        "x" * 73,  # one above the maximum
    ],
)
def test_password_policy_rejects_invalid_lengths(password):
    with pytest.raises(PasswordPolicyError):
        PasswordPolicy.validate(password)


def test_password_policy_error_mentions_allowed_range():
    with pytest.raises(PasswordPolicyError) as exc_info:
        PasswordPolicy.validate("short")
    message = str(exc_info.value)
    assert "8" in message and "72" in message


# ---------------------------------------------------------------------------
# Registration role whitelist
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw_role", "expected"),
    [
        ("buyer", RegistrationRole.BUYER),
        ("seller", RegistrationRole.SELLER),
    ],
)
def test_parse_registration_role_accepts_allowed_roles(raw_role, expected):
    assert parse_registration_role(raw_role) is expected


@pytest.mark.parametrize(
    "raw_role",
    [
        "admin",  # provisioned separately, never self-registered
        "Buyer",  # roles are lowercase exact
        "SELLER",
        "guest",
        "",
        None,
    ],
)
def test_parse_registration_role_rejects_disallowed_roles(raw_role):
    with pytest.raises(InvalidRoleError):
        parse_registration_role(raw_role)


def test_registration_role_values_are_lowercase():
    assert RegistrationRole.BUYER.value == "buyer"
    assert RegistrationRole.SELLER.value == "seller"


# ---------------------------------------------------------------------------
# Token policy (domain constants and expiry rule)
# ---------------------------------------------------------------------------


def test_access_token_ttl_is_thirty_minutes():
    assert ACCESS_TOKEN_TTL_SECONDS == 1800


def test_refresh_token_ttl_is_seven_days():
    assert REFRESH_TOKEN_TTL_SECONDS == 604800


def test_refresh_token_outlives_access_token():
    assert REFRESH_TOKEN_TTL_SECONDS > ACCESS_TOKEN_TTL_SECONDS


@pytest.mark.parametrize(
    ("elapsed_seconds", "expected_expired"),
    [
        (0, False),
        (1799, False),
        (1800, True),  # expiry is inclusive: at TTL the token is expired
        (1801, True),
    ],
)
def test_is_expired_respects_ttl_boundary(elapsed_seconds, expected_expired):
    issued_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = issued_at + timedelta(seconds=elapsed_seconds)
    assert is_expired(issued_at, now, ACCESS_TOKEN_TTL_SECONDS) is expected_expired


def test_is_expired_uses_utc_timestamps():
    issued_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = issued_at + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS + 1)
    assert is_expired(issued_at, now, REFRESH_TOKEN_TTL_SECONDS) is False
