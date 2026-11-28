"""Password hashing (scrypt) and signed access tokens (HS256), stdlib only."""

import base64
import hashlib
import hmac
import json
import secrets
import time

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${_b64e(salt)}${_b64e(digest)}"


def verify_password(password: str, stored: str | None) -> bool:
    """False for any malformed hash (for example the seed's placeholder)."""
    try:
        scheme, n, r, p, salt, digest = (stored or "").split("$")
        if scheme != "scrypt":
            return False
        expected = _b64d(digest)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_b64d(salt),
            n=int(n),
            r=int(r),
            p=int(p),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def create_token(user_id: int, secret: str, ttl_seconds: int, now: float | None = None) -> str:
    issued = int(now if now is not None else time.time())
    header = _b64e(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64e(
        json.dumps({"sub": str(user_id), "iat": issued, "exp": issued + ttl_seconds}).encode()
    )
    signature = hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64e(signature)}"


def decode_token(token: str, secret: str, now: float | None = None) -> int | None:
    """Return the user id for a valid, unexpired token, else None."""
    try:
        header, payload, signature = token.split(".")
        expected = hmac.new(
            secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(expected, _b64d(signature)):
            return None
        if json.loads(_b64d(header)).get("alg") != "HS256":
            return None
        claims = json.loads(_b64d(payload))
        if int(claims["exp"]) <= (now if now is not None else time.time()):
            return None
        return int(claims["sub"])
    except (ValueError, KeyError, TypeError):
        return None
