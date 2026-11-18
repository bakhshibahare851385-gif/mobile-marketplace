"""Authentication routes."""

from fastapi import APIRouter, Depends, Response, status

from app.api.v1.dependencies import (
    get_current_user,
    get_login_service,
    get_refresh_service,
    get_registration_service,
)
from app.api.v1.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPairResponse,
    UserResponse,
)
from app.application.auth.services import LoginService, RefreshService, RegistrationService
from app.application.auth.users import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    service: RegistrationService = Depends(get_registration_service),
) -> RegisterResponse:
    record = service.register(payload.email, payload.password, payload.role)
    return RegisterResponse(id=record.id, email=record.email, role=record.role)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    service: LoginService = Depends(get_login_service),
) -> LoginResponse:
    _, pair = service.login(payload.email, payload.password)
    return LoginResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
        refresh_expires_in=pair.refresh_expires_in,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(
    payload: RefreshRequest,
    service: RefreshService = Depends(get_refresh_service),
) -> TokenPairResponse:
    pair = service.refresh(payload.refresh_token)
    return TokenPairResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
        refresh_expires_in=pair.refresh_expires_in,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse(**current_user.__dict__)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: CurrentUser = Depends(get_current_user)) -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
