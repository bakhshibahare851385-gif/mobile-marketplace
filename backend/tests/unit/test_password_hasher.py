"""RED phase tests for password hashing (PLAN Step 2).

Expected to FAIL at collection: ``app.infrastructure.auth.password_hasher`` does
not exist yet. These tests pin the ``PasswordHasher`` contract used later by the
registration and login services.

Contract (docs/features/auth/SPEC.md, FR-AUTH-3):
  - hashing produces an Argon2id encoded string, never the plain password
  - hashing is salted (two hashes of the same password differ)
  - verification accepts the correct password and rejects wrong/corrupt hashes
  - verification never raises for malformed stored hashes
"""

import pytest

from app.infrastructure.auth.password_hasher import Argon2idPasswordHasher


@pytest.fixture
def hasher() -> Argon2idPasswordHasher:
    return Argon2idPasswordHasher()


def test_hash_returns_argon2id_encoded_string(hasher):
    hashed = hasher.hash("s3curePass!")

    assert isinstance(hashed, str)
    assert hashed.startswith("$argon2id$")
    assert hashed != "s3curePass!"


def test_hash_is_salted(hasher):
    first = hasher.hash("s3curePass!")
    second = hasher.hash("s3curePass!")

    assert first != second


def test_verify_accepts_correct_password(hasher):
    hashed = hasher.hash("s3curePass!")

    assert hasher.verify("s3curePass!", hashed) is True


@pytest.mark.parametrize("wrong_password", ["s3curePass", "S3curePass!", "wrong", ""])
def test_verify_rejects_wrong_password(hasher, wrong_password):
    hashed = hasher.hash("s3curePass!")

    assert hasher.verify(wrong_password, hashed) is False


@pytest.mark.parametrize(
    "malformed_hash",
    [
        "",
        "not-a-hash",
        "$argon2id$broken$fields",
        "$argon2i$v=19$m=65536,t=3,p=4$c2FsdA$c2FsdA",
    ],
)
def test_verify_returns_false_for_malformed_hash(hasher, malformed_hash):
    assert hasher.verify("s3curePass!", malformed_hash) is False


def test_verify_returns_false_for_non_string_hash(hasher):
    assert hasher.verify("s3curePass!", None) is False
