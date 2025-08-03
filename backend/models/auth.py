"""
Authentication models for user registration and login
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str
    name: Optional[str] = None

class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    """Response model for authentication operations"""
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional['UserInfo'] = None

class UserInfo(BaseModel):
    """User information model"""
    id: str
    email: str
    name: Optional[str] = None
    is_anonymous: bool
    created_at: str
    email_verified: bool = False

class TokenValidationResponse(BaseModel):
    """Response model for token validation"""
    valid: bool
    user: Optional[UserInfo] = None
    is_authenticated: bool = False
