"""
Authentication and authorization module for the medical health record system.
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from .models import User

logger = logging.getLogger(__name__)


class AuthManager:
    """Handles user authentication and authorization."""
    
    def __init__(self, secret_key: str = None):
        """Initialize the authentication manager."""
        self.secret_key = secret_key or secrets.token_hex(32)
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
    
    def hash_password(self, password: str) -> str:
        """Hash a password with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return stored_hash == password_hash_check.hex()
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def create_token(self, user: User) -> str:
        """Create a JWT token for a user."""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def has_permission(self, user_role: str, required_role: str) -> bool:
        """Check if a user has the required permissions."""
        role_hierarchy = {
            'user': 1,
            'doctor': 2,
            'admin': 3
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        return user_level >= required_level
    
    def require_auth(self, token: str, required_role: str = 'user') -> Optional[Dict[str, Any]]:
        """Decorator function to require authentication and authorization."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        if not self.has_permission(payload.get('role', 'user'), required_role):
            logger.warning(f"Insufficient permissions for user {payload.get('username')}")
            return None
        
        return payload