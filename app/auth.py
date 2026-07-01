"""JWT Authentication helpers for GPlan."""
from __future__ import annotations
import os
import hashlib
import bcrypt as _bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET", "gplan-super-secret-jwt-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

import hashlib
import bcrypt as _bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (via SHA256 pre-hash to avoid 72-byte limit)."""
    pwd_bytes = hashlib.sha256(password.encode()).hexdigest().encode()
    return _bcrypt.hashpw(pwd_bytes, _bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    pwd_bytes = hashlib.sha256(plain.encode()).hexdigest().encode()
    try:
        return _bcrypt.checkpw(pwd_bytes, hashed.encode())
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Returns user_id string or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
