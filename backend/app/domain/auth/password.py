"""Password policy rules for authentication."""


class PasswordPolicyError(ValueError):
    """Raised when a password does not satisfy the policy."""


class PasswordPolicy:
    """Length constraints applied to raw passwords before hashing."""

    MIN_LENGTH = 8
    MAX_LENGTH = 72

    @classmethod
    def validate(cls, password: str) -> None:
        if not isinstance(password, str):
            raise PasswordPolicyError("Password must be a string")
        if not cls.MIN_LENGTH <= len(password) <= cls.MAX_LENGTH:
            raise PasswordPolicyError(
                f"Password must be between {cls.MIN_LENGTH} and {cls.MAX_LENGTH} "
                "characters long"
            )
        return None
