"""Pydantic schemas for User."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ---- Request schemas ----

class UserSignup(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None


# ---- Response schemas ----

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
