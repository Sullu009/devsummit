from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .security import decode_token

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    role: str
    email: str


def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    token = None
    if creds is not None:
        token = creds.credentials
    if token is None:
        # allow gateway to forward identity via headers as a fallback
        token = request.headers.get("x-access-token")
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing authentication token")

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    return CurrentUser(id=payload["sub"], role=payload["role"], email=payload["email"])


def require_roles(*roles: str):
    allowed: Iterable[str] = roles

    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action")
        return user

    return _dep


def get_optional_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser | None:
    try:
        return get_current_user(request, creds)
    except HTTPException:
        return None
