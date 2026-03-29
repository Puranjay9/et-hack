"""Authentication routes — signup, login, refresh, logout."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_id,
)
from app.core.config import get_settings
from app.models.user import User
from app.schemas.user import (
    UserSignup,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshRequest,
)

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


async def get_redis():
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.close()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignup, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest,
    r: aioredis.Redis = Depends(get_redis),
):
    # Check if token is blacklisted
    is_blacklisted = await r.get(f"blacklist:{payload.refresh_token}")
    if is_blacklisted:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    token_data = decode_token(payload.refresh_token)
    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = token_data.get("sub")
    access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    # Blacklist the old refresh token
    await r.set(f"blacklist:{payload.refresh_token}", "1", ex=60 * 60 * 24 * 7)

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    refresh_token: RefreshRequest,
    r: aioredis.Redis = Depends(get_redis),
    user_id: str = Depends(get_current_user_id),
):
    await r.set(f"blacklist:{refresh_token.refresh_token}", "1", ex=60 * 60 * 24 * 7)
    return {"detail": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
