"""Request and response schemas for the authentication API."""

from typing import Literal

from pydantic import BaseModel, field_validator

from app.domain.auth.email import normalize_email
from app.domain.auth.password import PasswordPolicy


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: Literal["buyer", "seller"]

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        PasswordPolicy.validate(value)
        return value


class UserResponse(BaseModel):
    id: str
    email: str
    role: str


class RegisterResponse(UserResponse):
    pass


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int


class LoginResponse(TokenPairResponse):
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
