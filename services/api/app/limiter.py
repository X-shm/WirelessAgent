"""Rate limiter with Cloudflare CF-Connecting-IP support."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_real_ip(request: Request) -> str:
    cf = request.headers.get("CF-Connecting-IP")
    return cf if cf else get_remote_address(request)

limiter = Limiter(key_func=get_real_ip)
