"""Argon2id password hashing implementation."""

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import HashingError, InvalidHashError, VerificationError
from argon2.low_level import Type


class Argon2idPasswordHasher:
    """Hash and verify passwords using Argon2id.

    Plain passwords are never stored or returned; verification treats malformed
    stored hashes as a failed verification rather than raising.
    """

    def __init__(self) -> None:
        self._hasher = Argon2Hasher(type=Type.ID, hash_len=32, salt_len=16)

    def hash(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        if not isinstance(hashed_password, str) or not hashed_password:
            return False
        try:
            return bool(self._hasher.verify(hashed_password, plain_password))
        except (VerificationError, InvalidHashError, HashingError, ValueError, TypeError):
            return False
