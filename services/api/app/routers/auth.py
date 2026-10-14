import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenOut
from ..security import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _token(user: User) -> TokenOut:
    return TokenOut(access_token=create_token(user.id), user_id=user.id, display_name=user.display_name)


@router.post("/register", response_model=TokenOut)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_db)):
    email = body.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, detail="邮箱格式不正确")
    exists = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if exists:
        raise HTTPException(409, detail="该邮箱已被注册")
    name = (body.display_name or "").strip() or email.split("@")[0]
    user = User(email=email, password_hash=hash_password(body.password), display_name=name, is_guest=False)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _token(user)


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    email = body.email.strip().lower()
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, detail="邮箱或密码错误")
    return _token(user)


@router.post("/guest", response_model=TokenOut)
async def guest(db: AsyncSession = Depends(get_db)):
    email = f"guest_{uuid.uuid4().hex[:12]}@guest.local"
    user = User(email=email, password_hash=None, display_name="游客", is_guest=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _token(user)


@router.post("/logout")
async def logout():
    # 无状态 token：前端清除本地登录态即可；若需服务端失效可后续加黑名单。
    return {"ok": True}