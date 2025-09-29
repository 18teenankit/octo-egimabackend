from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import get_supabase
import logging
import base64
import hmac
import hashlib
import json

logger = logging.getLogger(__name__)

# Constants
# Use a stable, configurable admin auth cookie name
ADMIN_COOKIE_NAME = settings.ADMIN_COOKIE_NAME or "admin_session"

def is_admin_email(email: str) -> bool:
    """Return True only for the single configured admin email."""
    try:
        return email.lower() == settings.ALLOWED_ADMIN_EMAIL.lower()
    except Exception:  # pragma: no cover - defensive
        return False

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> tuple[Optional[dict], Optional[str]]:
    """Verify JWT token and return (payload, error_reason)."""
    if not token:
        return None, "missing_token"
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload, None
    except JWTError as exc:
        logger.debug("JWT decode failed: %s", exc)
        return None, "invalid_jwt"

async def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Extract user info from Auth0 token or session cookie."""
    
    # Method 1: Try Authorization header (session token from frontend)
    if credentials and credentials.credentials:
        try:
            token = credentials.credentials
            # Decode the base64 session token from frontend
            if token and len(token) > 20:
                try:
                    import base64
                    decoded = base64.b64decode(token).decode('utf-8')
                    session_data = json.loads(decoded)
                    email = session_data.get('email')
                    timestamp = session_data.get('timestamp', 0)
                    
                    # Check if email is admin and token is not too old (1 hour)
                    if email and is_admin_email(email):
                        token_age = (datetime.now().timestamp() * 1000) - timestamp
                        if token_age < 3600000:  # 1 hour in milliseconds
                            return {"email": email, "is_admin": True}
                except Exception as decode_error:
                    logger.debug(f"Failed to decode session token: {decode_error}")
        except Exception as e:
            logger.debug(f"Failed to validate session token: {e}")
    
    # Method 2: Try session cookie (fallback for browser requests)
    cookie_token = request.cookies.get(ADMIN_COOKIE_NAME)
    if cookie_token:
        try:
            email = verify_admin_session(cookie_token)
            if email and is_admin_email(email):
                return {"email": email, "is_admin": True}
        except Exception as e:
            logger.debug(f"Failed to validate session cookie: {e}")
    
    return None

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Require authenticated admin user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

async def log_admin_action(request: Request, user_email: str, action: str, details: dict = None):
    """AUTH DISABLED: No-op audit logging."""
    return None

# ---- Admin session HMAC token (to interop with Next middleware) ----
def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def sign_admin_session(email: str, ttl_seconds: int = 3600) -> str:
    """Create a compact HMAC token "payload.sig" matching frontend auth-session.ts.
    Payload is base64url(JSON: {email, iat, exp, v:1}); sig = HMAC-SHA256(secret, payloadB64).
    """
    if not settings.ADMIN_SESSION_SECRET:
        # Fallback: return empty to avoid setting incompatible cookie silently
        raise RuntimeError("ADMIN_SESSION_SECRET is not configured")
    now = int(datetime.now(timezone.utc).timestamp())
    payload = {
        "email": email,
        "iat": now,
        "exp": now + ttl_seconds,
        "v": 1,
    }
    payload_json = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = _b64url(payload_json)
    secret = settings.ADMIN_SESSION_SECRET.encode()
    sig = hmac.new(secret, payload_b64.encode(), hashlib.sha256).digest()
    sig_b64 = _b64url(sig)
    return f"{payload_b64}.{sig_b64}"

def verify_admin_session(token: str) -> Optional[str]:
    """Verify HMAC admin session cookie and return email if valid."""
    if not token or "." not in token or not settings.ADMIN_SESSION_SECRET:
        return None
    payload_b64, sig_b64 = token.split(".", 1)
    # Recompute signature
    expected_sig = hmac.new(settings.ADMIN_SESSION_SECRET.encode(), payload_b64.encode(), hashlib.sha256).digest()
    # Constant-time compare
    if not hmac.compare_digest(_b64url(expected_sig), sig_b64):
        return None
    # Decode payload
    # Pad base64
    pad = "=" * (-len(payload_b64) % 4)
    try:
        payload_json = base64.urlsafe_b64decode((payload_b64 + pad).encode()).decode()
        payload = json.loads(payload_json)
        exp = int(payload.get("exp", 0))
        now = int(datetime.now(timezone.utc).timestamp())
        if now >= exp:
            return None
        email = payload.get("email")
        if isinstance(email, str) and email:
            return email
        return None
    except Exception:
        return None