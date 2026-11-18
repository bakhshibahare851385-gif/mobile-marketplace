"""Registration role whitelist for authentication."""

from enum import Enum


class InvalidRoleError(ValueError):
    """Raised when a role is not allowed for self-registration."""


class RegistrationRole(str, Enum):
    """Roles a visitor may choose when registering."""

    BUYER = "buyer"
    SELLER = "seller"


def parse_registration_role(raw: str | None) -> RegistrationRole:
    """Parse a registration role, rejecting admins and unknown values."""
    if not isinstance(raw, str):
        raise InvalidRoleError("Role must be a string")
    try:
        return RegistrationRole(raw)
    except ValueError as exc:
        raise InvalidRoleError(f"Unsupported registration role: {raw!r}") from exc
