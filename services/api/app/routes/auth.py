"""Auth routes 鈥?register, login, JWT token issuance."""
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.config import settings
from jose import jwt
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta


router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hash_str: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_str.encode())


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    is_guest: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    display_name: str


def create_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user.id, "email": user.email, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(user)
    return TokenResponse(access_token=token, user_id=user.id, display_name=user.display_name, is_guest=False)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user)
    return TokenResponse(access_token=token, user_id=user.id, display_name=user.display_name, is_guest=False)


class GuestRequest(BaseModel):
    pass  # no fields needed


@router.post("/guest", response_model=TokenResponse)
async def guest(db: AsyncSession = Depends(get_db)):
    """Create a temporary guest user and return a token."""
    import uuid
    guest_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"guest-{guest_id}@anonymous.local",
        password_hash=hash_password(uuid.uuid4().hex),
        display_name=f"Guest-{guest_id}",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_token(user)
    return TokenResponse(access_token=token, user_id=user.id, display_name=user.display_name, is_guest=True)