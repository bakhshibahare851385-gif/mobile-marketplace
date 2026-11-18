"""RED phase tests for the SQLite User model and repository (PLAN Step 3).

Expected to FAIL at collection: the application DTOs and the infrastructure
database modules do not exist yet. These tests pin the repository contract used
later by the registration/login services.

Contract (docs/features/auth/SPEC.md, FR-AUTH-2/3):
  - create persists a normalized email, an Argon2id hash string, and a role
  - the model has no plain-text password column
  - find_by_email normalizes its input and is case-insensitive
  - duplicate emails raise DuplicateEmailError without creating a second row
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.auth.errors import DuplicateEmailError
from app.application.auth.users import NewUser
from app.domain.auth.email import Email
from app.domain.auth.role import RegistrationRole
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user import User
from app.infrastructure.db.repositories.user import SqliteUserRepository


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db_session:
        yield db_session


@pytest.fixture
def repository(session):
    return SqliteUserRepository(session)


def make_new_user(
    email: str = "Buyer@Example.COM",
    password_hash: str = "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$cmVhbGhhc2g",
    role: RegistrationRole = RegistrationRole.BUYER,
) -> NewUser:
    return NewUser(email=Email(email), password_hash=password_hash, role=role)


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------


def test_create_persists_user_with_normalized_email(repository):
    record = repository.create(make_new_user())

    assert record.email == "buyer@example.com"
    assert record.role == "buyer"
    assert record.password_hash.startswith("$argon2id$")
    assert record.is_active is True
    assert record.last_login_at is None
    assert isinstance(record.id, str) and record.id


def test_create_assigns_distinct_ids(repository):
    first = repository.create(make_new_user("first@example.com"))
    second = repository.create(make_new_user("second@example.com"))

    assert first.id != second.id


def test_user_model_has_no_plain_password_column():
    column_names = set(User.__table__.columns.keys())

    assert "password_hash" in column_names
    assert "password" not in column_names


def test_create_does_not_store_plain_password(repository, session):
    plain_password = "s3curePass!"
    repository.create(make_new_user(password_hash="$argon2id$stored-hash"))

    stored_hashes = [row.password_hash for row in session.query(User).all()]
    assert stored_hashes == ["$argon2id$stored-hash"]
    assert plain_password not in stored_hashes


# ---------------------------------------------------------------------------
# Lookup by email
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "lookup",
    [
        "buyer@example.com",
        "BUYER@EXAMPLE.COM",
        "  Buyer@Example.com  ",
        Email("buyer@example.com"),
    ],
)
def test_find_by_email_normalizes_lookup(repository, lookup):
    created = repository.create(make_new_user())

    found = repository.find_by_email(lookup)

    assert found is not None
    assert found.id == created.id


def test_find_by_email_returns_none_for_unknown_address(repository):
    repository.create(make_new_user())

    assert repository.find_by_email("nobody@example.com") is None


def test_get_by_id_returns_the_matching_user(repository):
    created = repository.create(make_new_user())

    found = repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.email == "buyer@example.com"


def test_get_by_id_returns_none_for_unknown_id(repository):
    assert repository.get_by_id("does-not-exist") is None


# ---------------------------------------------------------------------------
# Duplicate email handling
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "duplicate_email",
    [
        "buyer@example.com",
        "BUYER@EXAMPLE.COM",
        " Buyer@Example.com ",
    ],
)
def test_duplicate_email_raises_domain_error(repository, duplicate_email):
    repository.create(make_new_user())

    with pytest.raises(DuplicateEmailError):
        repository.create(make_new_user(email=duplicate_email))


def test_duplicate_create_does_not_persist_a_second_row(repository, session):
    repository.create(make_new_user())

    with pytest.raises(DuplicateEmailError):
        repository.create(make_new_user())

    assert session.query(User).count() == 1
