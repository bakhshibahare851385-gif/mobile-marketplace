"""FastAPI application entrypoint."""

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.application.auth.errors import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidTokenError,
    UnauthorizedError,
)

app = FastAPI(title="Mobile Accessories Marketplace API", version="0.1.0")
app.include_router(auth_router, prefix="/api/v1")


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Single source of truth for marketplace error envelopes."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": str(uuid4()),
            }
        },
    )


@app.exception_handler(DuplicateEmailError)
async def duplicate_email_handler(request: Request, exc: DuplicateEmailError) -> JSONResponse:
    return _error_response(409, "duplicate_email", str(exc))


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return _error_response(401, "invalid_credentials", str(exc))


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return _error_response(401, "unauthorized", str(exc))


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    return _error_response(401, "invalid_token", str(exc))
