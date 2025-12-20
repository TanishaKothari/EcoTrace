"""
Security utilities for token generation and validation
"""

import secrets
import hashlib
import hmac
import time
from dotenv import load_dotenv
import os
from typing import Optional
import base64
import json

# Secret key for signing tokens
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Please create a backend/.env file with: SECRET_KEY=your_secret_key_here"
    )

def generate_secure_anonymous_token() -> str:
    """Generate a cryptographically secure anonymous user token"""
    # Generate random bytes
    random_bytes = secrets.token_bytes(32)
    
    # Create timestamp
    timestamp = int(time.time())
    
    # Create payload
    payload = {
        "type": "anonymous",
        "created": timestamp,
        "random": base64.b64encode(random_bytes).decode()
    }
    
    # Encode payload
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
    
    # Create signature
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()[:16]  # Use first 16 chars for shorter tokens
    
    # Combine into token
    token = f"anon_{payload_b64}_{signature}"
    
    return token

def validate_token(token: str) -> bool:
    """Validate that a token is properly signed and formatted"""
    try:
        # Handle both anonymous and authenticated tokens
        if not (token.startswith("anon_") or token.startswith("auth_")):
            return False

        parts = token.split("_", 2)
        if len(parts) != 3:
            return False

        token_type, payload_b64, signature = parts
        
        # Verify signature
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if not hmac.compare_digest(signature, expected_signature):
            return False
        
        # Decode and validate payload
        # Add padding if needed
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += '=' * padding
            
        payload_json = base64.urlsafe_b64decode(payload_b64).decode()
        payload = json.loads(payload_json)
        
        # Validate payload structure based on token type
        expected_type = "anonymous" if token_type == "anon" else "authenticated"
        if payload.get("type") != expected_type:
            return False
        
        # Validate required fields based on token type
        if token_type == "anon":
            if "created" not in payload or "random" not in payload:
                return False
        else:  # auth token
            if "user_id" not in payload or "created" not in payload or "random" not in payload:
                return False
        
        # Note: No expiration for anonymous tokens to maintain persistent history
        # In Phase 2, authenticated tokens could have expiration
        
        return True

    except Exception:
        return False

def hash_token_for_storage(token: str) -> str:
    """Hash token for secure database storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def extract_token_info(token: str) -> Optional[dict]:
    """Extract information from a valid token"""
    if not validate_token(token):
        return None
    
    try:
        parts = token.split("_", 2)
        payload_b64 = parts[1]
        
        # Add padding if needed
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += '=' * padding
            
        payload_json = base64.urlsafe_b64decode(payload_b64).decode()
        return json.loads(payload_json)
    except Exception:
        return None
