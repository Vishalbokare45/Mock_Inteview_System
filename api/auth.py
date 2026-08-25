import hashlib
import hmac
import os
import secrets
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.database import Database

security = HTTPBearer()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$", 1)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_token(user_id: str) -> str:
    # Simple signed token for this application. Replace with a dedicated JWT library in production.
    expires = str(int(time.time()) + 60 * 60 * 24)
    payload = f"{user_id}.{expires}"
    secret = os.getenv("AUTH_SECRET", "change-this-secret")
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(Database),
) -> dict:
    try:
        user_id, expires, signature = credentials.credentials.split(".", 2)
        payload = f"{user_id}.{expires}"
        secret = os.getenv("AUTH_SECRET", "change-this-secret")
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if int(expires) < int(time.time()) or not hmac.compare_digest(signature, expected):
            raise ValueError
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
