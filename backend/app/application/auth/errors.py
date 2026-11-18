"""Authentication error types shared by services and the API layer."""


class AuthenticationError(Exception):
    """Base class for authentication failures."""


class InvalidTokenError(AuthenticationError):
    """The token is malformed, badly signed, or no longer usable."""


class ExpiredTokenError(InvalidTokenError):
    """The token's lifetime has elapsed."""


class UnexpectedTokenTypeError(InvalidTokenError):
    """The token type does not match the operation being attempted."""


class DuplicateEmailError(AuthenticationError):
    """An account with this normalized email already exists."""


class InvalidCredentialsError(AuthenticationError):
    """The supplied email or password did not match an account."""


class UnauthorizedError(AuthenticationError):
    """The request lacks valid authentication credentials."""
