"""RED phase tests for the role guard (PLAN Step 6).

Expected to FAIL at collection: the guard and CurrentUser DTO do not exist yet.
"""

import pytest
from fastapi import HTTPException

from app.application.auth.guards import require_roles
from app.application.auth.users import CurrentUser


def test_require_roles_allows_matching_role():
    guard = require_roles("seller")
    seller = CurrentUser(id="u-1", email="seller@example.com", role="seller")

    assert guard(seller) is seller


def test_require_roles_rejects_wrong_role():
    guard = require_roles("seller")
    buyer = CurrentUser(id="u-2", email="buyer@example.com", role="buyer")

    with pytest.raises(HTTPException) as exc_info:
        guard(buyer)

    assert exc_info.value.status_code == 403


def test_require_roles_accepts_multiple_allowed_roles():
    guard = require_roles("seller", "admin")
    admin = CurrentUser(id="u-3", email="admin@example.com", role="admin")

    assert guard(admin) is admin
