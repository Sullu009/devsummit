"""
Shared authentication utilities.

Every service trusts the SAME JWT_SECRET (set via env var, shared across
services through docker-compose / .env). Identity Service is the only
service that *issues* tokens; every other service only *verifies* them.
This keeps auth logic consistent without a network call per request.
"""
from __future__ import annotations

import os
import time
import uuid
from typing import Any, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TTL_SECONDS = int(os.environ.get("ACCESS_TOKEN_TTL_SECONDS", "3600"))
REFRESH_TOKEN_TTL_SECONDS = int(os.environ.get("REFRESH_TOKEN_TTL_SECONDS", str(60 * 60 * 24 * 14)))

_hasher = PasswordHasher()


def hash_password(raw: str) -> str:
    return _hasher.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, raw)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def create_access_token(user_id: str, role: str, email: str) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "type": "access",
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL_SECONDS,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + REFRESH_TOKEN_TTL_SECONDS,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
