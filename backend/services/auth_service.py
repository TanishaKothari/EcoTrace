"""
Authentication service for user registration and login
"""

import hashlib
import secrets
import hmac
import time
import base64
import json
from typing import Optional, Tuple
from database import get_db_session, User
from utils.security import hash_token_for_storage, validate_token, SECRET_KEY

class AuthService:
    """Service for handling user authentication"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(":")
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return hmac.compare_digest(password_hash, computed_hash)
        except ValueError:
            return False
    
    def generate_auth_token(self, user_id: str) -> str:
        """Generate authenticated user token"""
        timestamp = int(time.time())
        payload = {
            "type": "authenticated",
            "user_id": user_id,
            "created": timestamp,
            "random": secrets.token_hex(16)
        }
        
        # Encode payload
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
        
        # Create signature
        signature = hmac.new(
            self.secret_key.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return f"auth_{payload_b64}_{signature}"
    
    def validate_auth_token(self, token: str) -> Optional[str]:
        """Validate authenticated token and return user_id"""
        try:
            if not token.startswith("auth_"):
                return None
            
            parts = token.split("_", 2)
            if len(parts) != 3:
                return None
            
            _, payload_b64, signature = parts
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Decode payload
            padding = 4 - (len(payload_b64) % 4)
            if padding != 4:
                payload_b64 += '=' * padding
                
            payload_json = base64.urlsafe_b64decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            if payload.get("type") != "authenticated":
                return None
            
            return payload.get("user_id")
            
        except Exception:
            return None
    
    def register_user(self, email: str, password: str, name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Register a new user account"""
        db = get_db_session()
        try:
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == email.lower()).first()
            if existing_user:
                return False, "Email already registered", None
            
            # Validate password strength
            if len(password) < 6:
                return False, "Password must be at least 6 characters", None
            
            # Create new authenticated user
            user_id = f"user_{secrets.token_hex(8)}"
            password_hash = self.hash_password(password)
            
            user = User(
                id=user_id,
                token_hash="",  # Will be set when they login
                is_anonymous=False,
                email=email.lower(),
                password_hash=password_hash,
                name=name,
                email_verified=False
            )
            
            db.add(user)
            db.commit()
            
            # Generate auth token
            auth_token = self.generate_auth_token(user_id)
            
            # Update token hash
            user.token_hash = hash_token_for_storage(auth_token)
            db.commit()
            
            return True, "Account created successfully", auth_token
            
        except Exception as e:
            db.rollback()
            return False, f"Registration failed: {str(e)}", None
        finally:
            db.close()
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """Login user and return auth token"""
        db = get_db_session()
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email.lower()).first()
            if not user or user.is_anonymous:
                return False, "Invalid email or password", None
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                return False, "Invalid email or password", None
            
            # Generate new auth token
            auth_token = self.generate_auth_token(user.id)
            
            # Update token hash and last active
            user.token_hash = hash_token_for_storage(auth_token)
            user.last_active = db.query(User).filter(User.id == user.id).first().last_active
            db.commit()
            
            return True, "Login successful", auth_token
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None
        finally:
            db.close()
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """Get user by any valid token (anonymous or authenticated)"""
        db = get_db_session()
        try:
            # Check if it's an authenticated token
            user_id = self.validate_auth_token(token)
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user and not user.is_anonymous:
                    return user
            
            # Check if it's a valid anonymous token
            if validate_token(token):
                token_hash = hash_token_for_storage(token)
                user = db.query(User).filter(User.token_hash == token_hash).first()
                if user and user.is_anonymous:
                    return user
            
            return None
        finally:
            db.close()
    
    def is_authenticated_user(self, token: str) -> bool:
        """Check if token belongs to an authenticated user"""
        user = self.get_user_by_token(token)
        return user is not None and not user.is_anonymous

# Global instance
auth_service = AuthService()
