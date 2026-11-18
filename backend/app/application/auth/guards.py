"""Role-based authorization guard."""

from collections.abc import Callable

from fastapi import HTTPException

from app.application.auth.users import CurrentUser


def require_roles(*allowed_roles: str) -> Callable[[CurrentUser], CurrentUser]:
    """Return a guard allowing only the listed roles."""

    def guard(current_user: CurrentUser) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return guard
