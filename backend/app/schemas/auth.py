"""
Authentication schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    email: str | None = None
    user_id: int | None = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    role: str
    
    class Config:
        from_attributes = True
