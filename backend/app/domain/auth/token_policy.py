"""Token lifetime policy for access and refresh JWTs."""

from datetime import datetime, timedelta

ACCESS_TOKEN_TTL_SECONDS = 1800  # 30 minutes
REFRESH_TOKEN_TTL_SECONDS = 604800  # 7 days


def is_expired(issued_at: datetime, now: datetime, ttl_seconds: int) -> bool:
    """Return True once ``ttl_seconds`` have elapsed since issuance."""
    return now >= issued_at + timedelta(seconds=ttl_seconds)
