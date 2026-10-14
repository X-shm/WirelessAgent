"""密码哈希与 token：全部用标准库实现（无第三方依赖）。

- 密码：PBKDF2-HMAC-SHA256，120000 次迭代
- token：HMAC-SHA256 签名，格式 <payload>.<signature>，payload 含 uid 与 exp
"""
import base64
import hashlib
import hmac
import json
import os
import time

from .config import settings

_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return "pbkdf2$%d$%s$%s" % (
        _ITERATIONS,
        base64.b64encode(salt).decode(),
        base64.b64encode(dk).decode(),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_b64, hash_b64 = stored.split("$")
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def create_token(user_id: int) -> str:
    payload = {"uid": user_id, "exp": int(time.time()) + settings.TOKEN_TTL_SECONDS}
    body = _b64url(json.dumps(payload).encode())
    sig = _b64url(hmac.new(settings.SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    return body + "." + sig


def decode_token(token: str):
    """返回 user_id；无效 / 过期返回 None。"""
    try:
        body, sig = token.split(".")
        expected = _b64url(hmac.new(settings.SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64url_decode(body))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return int(payload["uid"])
    except Exception:
        return None