"""RED phase integration tests for POST /api/v1/auth/register (PLAN Step 4).

Expected to FAIL at collection: ``app.main`` and the API/database wiring do not
exist yet. These tests pin the HTTP contract for registration.

Contract (docs/features/auth/SPEC.md, AC-1/2/3, FR-AUTH-1/2/3/4):
  - 201 with exactly {id, email, role}; email normalized; no hash or password leaked
  - 422 for malformed email, weak/too-long password, disallowed role, missing fields
  - 409 with error envelope for duplicate emails (any casing); no second row
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import JWT_SECRET_KEY
from app.infrastructure.auth.password_hasher import Argon2idPasswordHasher
from app.infrastructure.auth.token_service import JwtTokenService
from app.infrastructure.db.base import Base
from app.infrastructure.db.database import get_session
from app.infrastructure.db.models.user import User
from app.main import app

REGISTER_URL = "/api/v1/auth/register"


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db_session:
        yield db_session


@pytest.fixture
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def valid_registration(**overrides):
    payload = {
        "email": " Buyer@Example.COM ",
        "password": "s3curePass!",
        "role": "buyer",
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Success
# ---------------------------------------------------------------------------


def test_register_returns_201_with_only_public_fields(client):
    response = client.post(REGISTER_URL, json=valid_registration())

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "role"}
    assert isinstance(body["id"], str) and body["id"]
    assert body["email"] == "buyer@example.com"
    assert body["role"] == "buyer"


def test_register_normalizes_email_before_persisting(client, session):
    client.post(REGISTER_URL, json=valid_registration())

    stored = session.query(User).one()
    assert stored.email == "buyer@example.com"


def test_register_persists_argon2id_hash_not_plain_password(client, session):
    plain_password = "s3curePass!"
    client.post(REGISTER_URL, json=valid_registration(password=plain_password))

    stored = session.query(User).one()
    assert stored.password_hash != plain_password
    assert stored.password_hash.startswith("$argon2id$")
    assert Argon2idPasswordHasher().verify(plain_password, stored.password_hash) is True


def test_register_accepts_seller_role(client):
    response = client.post(
        REGISTER_URL,
        json=valid_registration(email="seller@example.com", role="seller"),
    )

    assert response.status_code == 201
    assert response.json()["role"] == "seller"


def test_register_response_never_exposes_password_hash(client):
    response = client.post(REGISTER_URL, json=valid_registration())

    assert "password" not in response.text
    assert "password_hash" not in response.text
    assert "$argon2id$" not in response.text


# ---------------------------------------------------------------------------
# Invalid input -> 422
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_payload",
    [
        valid_registration(email="not-an-email"),
        valid_registration(email=""),
        valid_registration(password="short"),
        valid_registration(password="x" * 73),
        valid_registration(role="admin"),
        valid_registration(role="Buyer"),
        {"password": "s3curePass!", "role": "buyer"},  # missing email
        {"email": "buyer@example.com", "role": "buyer"},  # missing password
        {"email": "buyer@example.com", "password": "s3curePass!"},  # missing role
    ],
)
def test_register_rejects_invalid_payload_with_422(client, bad_payload, session):
    response = client.post(REGISTER_URL, json=bad_payload)

    assert response.status_code == 422
    assert "detail" in response.json()
    assert session.query(User).count() == 0


# ---------------------------------------------------------------------------
# Duplicate email -> 409
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "duplicate_email",
    [
        "buyer@example.com",
        "BUYER@EXAMPLE.COM",
        " Buyer@Example.com ",
    ],
)
def test_register_duplicate_email_returns_409(client, session, duplicate_email):
    assert client.post(REGISTER_URL, json=valid_registration()).status_code == 201

    response = client.post(
        REGISTER_URL,
        json=valid_registration(email=duplicate_email, password="anotherPass1!"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_email"
    assert session.query(User).count() == 1


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

LOGIN_URL = "/api/v1/auth/login"


def register_user(
    client,
    email: str = "buyer@example.com",
    password: str = "s3curePass!",
    role: str = "buyer",
):
    response = client.post(
        REGISTER_URL,
        json={"email": email, "password": password, "role": role},
    )
    assert response.status_code == 201
    return response.json()


def decode_token(token: str, expected_type: str):
    return JwtTokenService(secret=JWT_SECRET_KEY).decode(token, expected_type)


def test_login_returns_200_with_access_and_refresh_tokens(client):
    user = register_user(client)

    response = client.post(
        LOGIN_URL, json={"email": user["email"], "password": "s3curePass!"}
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "access_token",
        "refresh_token",
        "token_type",
        "expires_in",
        "refresh_expires_in",
    }
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 1800
    assert body["refresh_expires_in"] == 604800
    assert body["access_token"] and body["refresh_token"]
    assert body["access_token"] != body["refresh_token"]


def test_login_tokens_contain_expected_claims(client):
    user = register_user(client)

    body = client.post(
        LOGIN_URL, json={"email": "buyer@example.com", "password": "s3curePass!"}
    ).json()
    access = decode_token(body["access_token"], "access")
    refresh = decode_token(body["refresh_token"], "refresh")

    assert access.subject == user["id"]
    assert access.role == "buyer"
    assert access.token_type == "access"
    assert refresh.subject == user["id"]
    assert refresh.token_type == "refresh"


def test_login_for_seller_embeds_seller_role(client):
    register_user(client, email="seller@example.com", role="seller")

    body = client.post(
        LOGIN_URL, json={"email": "seller@example.com", "password": "s3curePass!"}
    ).json()

    assert decode_token(body["access_token"], "access").role == "seller"


def test_login_normalizes_email(client):
    register_user(client, email="Buyer@Example.COM")

    response = client.post(
        LOGIN_URL,
        json={"email": "  BUYER@EXAMPLE.COM  ", "password": "s3curePass!"},
    )

    assert response.status_code == 200


def test_login_updates_last_login_at(client, session):
    register_user(client)

    client.post(
        LOGIN_URL, json={"email": "buyer@example.com", "password": "s3curePass!"}
    )

    assert session.query(User).one().last_login_at is not None


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("buyer@example.com", "wrongPassword1!"),
        ("nobody@example.com", "s3curePass!"),
    ],
)
def test_login_rejects_bad_credentials_with_generic_401(client, email, password):
    register_user(client)

    response = client.post(LOGIN_URL, json={"email": email, "password": password})

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "invalid_credentials"
    assert "access_token" not in body
    assert "refresh_token" not in body


def test_login_failure_message_is_identical_for_both_failure_modes(client):
    register_user(client)

    wrong_password = client.post(
        LOGIN_URL, json={"email": "buyer@example.com", "password": "wrongPassword1!"}
    ).json()
    unknown_email = client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "s3curePass!"}
    ).json()

    assert wrong_password["error"]["message"] == unknown_email["error"]["message"]
    assert "buyer@example.com" not in wrong_password["error"]["message"]
    assert "nobody@example.com" not in unknown_email["error"]["message"]


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"password": "s3curePass!"},
        {"email": "buyer@example.com"},
        {},
    ],
)
def test_login_rejects_incomplete_payload_with_422(client, bad_payload):
    response = client.post(LOGIN_URL, json=bad_payload)

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Step 6: /auth/me, /auth/logout, /auth/refresh
# ---------------------------------------------------------------------------

ME_URL = "/api/v1/auth/me"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"


def login_user(client, email: str = "buyer@example.com", password: str = "s3curePass!"):
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def expired_token(token_type: str, user_id: str) -> str:
    age = timedelta(hours=1) if token_type == "access" else timedelta(days=8)
    past = datetime.now(timezone.utc) - age
    service = JwtTokenService(secret=JWT_SECRET_KEY, clock=lambda: past)
    if token_type == "access":
        return service.issue_access(user_id, "buyer")
    return service.issue_refresh(user_id)


# -- /auth/me ---------------------------------------------------------------


def test_me_returns_current_user_for_valid_access_token(client):
    user = register_user(client)
    tokens = login_user(client)

    response = client.get(ME_URL, headers=bearer(tokens["access_token"]))

    assert response.status_code == 200
    assert response.json() == {
        "id": user["id"],
        "email": "buyer@example.com",
        "role": "buyer",
    }


def test_me_rejects_missing_token(client):
    assert client.get(ME_URL).status_code == 401


def test_me_rejects_refresh_token_used_as_bearer(client):
    register_user(client)
    tokens = login_user(client)

    response = client.get(ME_URL, headers=bearer(tokens["refresh_token"]))

    assert response.status_code == 401


@pytest.mark.parametrize("token_type", ["access", "refresh"])
def test_me_rejects_expired_token(client, token_type):
    user = register_user(client)
    token = expired_token(token_type, user["id"])

    assert client.get(ME_URL, headers=bearer(token)).status_code == 401


def test_me_rejects_tampered_token(client):
    register_user(client)
    tokens = login_user(client)
    token = tokens["access_token"]
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    assert client.get(ME_URL, headers=bearer(tampered)).status_code == 401


# -- /auth/logout -----------------------------------------------------------


def test_logout_returns_204_for_valid_token(client):
    register_user(client)
    tokens = login_user(client)

    response = client.post(LOGOUT_URL, headers=bearer(tokens["access_token"]))

    assert response.status_code == 204
    assert response.text == ""


def test_logout_requires_token(client):
    assert client.post(LOGOUT_URL).status_code == 401


# -- /auth/refresh ----------------------------------------------------------


def test_refresh_returns_new_token_pair(client):
    register_user(client)
    tokens = login_user(client)

    response = client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "access_token",
        "refresh_token",
        "expires_in",
        "refresh_expires_in",
    }
    assert body["access_token"] != tokens["access_token"]
    assert body["refresh_token"] != tokens["refresh_token"]
    assert body["expires_in"] == 1800
    assert body["refresh_expires_in"] == 604800


def test_refreshed_access_token_works_on_me(client):
    register_user(client)
    tokens = login_user(client)
    refreshed = client.post(
        REFRESH_URL, json={"refresh_token": tokens["refresh_token"]}
    ).json()

    response = client.get(ME_URL, headers=bearer(refreshed["access_token"]))

    assert response.status_code == 200
    assert response.json()["email"] == "buyer@example.com"


def test_old_refresh_token_cannot_be_reused(client):
    register_user(client)
    tokens = login_user(client)
    assert client.post(
        REFRESH_URL, json={"refresh_token": tokens["refresh_token"]}
    ).status_code == 200

    response = client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 401


def test_new_refresh_token_can_be_rotated_again(client):
    register_user(client)
    tokens = login_user(client)
    first = client.post(
        REFRESH_URL, json={"refresh_token": tokens["refresh_token"]}
    ).json()

    second = client.post(REFRESH_URL, json={"refresh_token": first["refresh_token"]})

    assert second.status_code == 200


def test_refresh_rejects_access_token(client):
    register_user(client)
    tokens = login_user(client)

    response = client.post(REFRESH_URL, json={"refresh_token": tokens["access_token"]})

    assert response.status_code == 401


def test_refresh_rejects_expired_token(client):
    user = register_user(client)

    response = client.post(
        REFRESH_URL, json={"refresh_token": expired_token("refresh", user["id"])}
    )

    assert response.status_code == 401


@pytest.mark.parametrize("bad_token", ["not-a-jwt", "", "a.b.c"])
def test_refresh_rejects_malformed_token(client, bad_token):
    response = client.post(REFRESH_URL, json={"refresh_token": bad_token})

    assert response.status_code == 401


def test_refresh_rejects_missing_token_field(client):
    response = client.post(REFRESH_URL, json={})

    assert response.status_code == 422
