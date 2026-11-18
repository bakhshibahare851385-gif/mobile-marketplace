"""Email normalization and validation for authentication."""

from dataclasses import dataclass


class InvalidEmailError(ValueError):
    """Raised when an email address is missing or malformed."""


def normalize_email(raw: str | None) -> str:
    """Return the canonical form of an email address.

    Canonicalization trims surrounding whitespace and lowercases the whole
    address, including plus-tags. The address must have exactly one ``@``, a
    non-empty local part, and a dotted domain with non-empty labels.
    """
    if not isinstance(raw, str):
        raise InvalidEmailError("Email must be a string")

    value = raw.strip().lower()
    if not value:
        raise InvalidEmailError("Email must not be empty")
    if any(character.isspace() for character in value):
        raise InvalidEmailError("Email must not contain whitespace")

    parts = value.split("@")
    if len(parts) != 2:
        raise InvalidEmailError("Email must contain exactly one '@'")

    local, domain = parts
    if not local or not domain:
        raise InvalidEmailError("Email must have a local part and a domain")

    labels = domain.split(".")
    if len(labels) < 2 or any(not label for label in labels):
        raise InvalidEmailError("Email domain must contain at least two labels")

    return value


@dataclass(frozen=True, repr=False)
class Email:
    """A validated, normalized email address."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", normalize_email(self.value))

    def __repr__(self) -> str:
        return f"Email({self.value!r})"
