"""
Auth0 JWT Token Validation for FastAPI Backend
Validates Auth0 access tokens using RS256 algorithm with public key verification
"""
import logging
from typing import Optional
from functools import lru_cache
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# Auth0 Configuration
AUTH0_DOMAIN = settings.NEXT_PUBLIC_AUTH0_DOMAIN if hasattr(settings, 'NEXT_PUBLIC_AUTH0_DOMAIN') else "cortejtech.us.auth0.com"
# Use custom API audience for proper JWT validation
AUTH0_AUDIENCE = getattr(settings, 'AUTH0_AUDIENCE', "https://cortejtech-api.local")
ALGORITHMS = ["RS256"]

# Development mode configuration
SKIP_AUDIENCE_CHECK = settings.ENVIRONMENT == "development" and settings.DEBUG

logger.info(f"🔐 Auth0 Configuration: domain={AUTH0_DOMAIN}, audience={AUTH0_AUDIENCE}, skip_audience={SKIP_AUDIENCE_CHECK}")

@lru_cache(maxsize=1)
def get_auth0_jwks():
    """Fetch and cache Auth0 JSON Web Key Set (JWKS) for token validation"""
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        logger.info(f"📡 Fetching Auth0 JWKS from: {jwks_url}")
        with httpx.Client() as client:
            response = client.get(jwks_url, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            logger.info(f"✅ Successfully fetched JWKS with {len(jwks.get('keys', []))} keys")
            return jwks
    except Exception as e:
        logger.error(f"❌ Failed to fetch Auth0 JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )

def get_auth0_public_key(token: str):
    """Extract the public key from Auth0 JWKS based on token's kid (key ID)"""
    try:
        # Decode header without verification to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        logger.debug(f"🔑 Token kid: {kid}")
        
        jwks = get_auth0_jwks()
        
        # Find the key with matching kid
        for key in jwks.get("keys", []):
            if key["kid"] == kid:
                logger.debug(f"✅ Found matching public key for kid: {kid}")
                return key
        
        logger.error(f"❌ No matching public key found for kid: {kid}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: Public key not found"
        )
    except JWTError as e:
        logger.error(f"❌ JWT header decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

def verify_auth0_token(token: str) -> dict:
    """
    Verify Auth0 JWT token (ID token or access token) and return decoded payload
    
    Validates:
    - Token signature using Auth0 public key (RS256)
    - Token expiration
    - Token issuer (Auth0 domain)
    - Token audience (client ID for ID tokens, API audience for access tokens)
    
    Returns decoded token payload with user info
    """
    try:
        # Get the public key
        public_key = get_auth0_public_key(token)
        
        # Prepare verification options
        verify_options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": not SKIP_AUDIENCE_CHECK,  # Skip audience check in development
            "require_exp": True,
            "require_iat": True,
        }
        
        # Try to decode without audience first to check token type
        unverified_payload = jwt.get_unverified_claims(token)
        audience = unverified_payload.get('aud')
        
        # Determine expected audience based on token type
        # ID tokens have client_id as audience, access tokens have API audience
        expected_audience = None
        if not SKIP_AUDIENCE_CHECK:
            if isinstance(audience, str) and audience == settings.NEXT_PUBLIC_AUTH0_CLIENT_ID:
                # This is an ID token
                expected_audience = settings.NEXT_PUBLIC_AUTH0_CLIENT_ID
                logger.debug("🆔 Detected ID token")
            else:
                # This is an access token
                expected_audience = AUTH0_AUDIENCE
                logger.debug("🎫 Detected access token")
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=ALGORITHMS,
            audience=expected_audience,
            issuer=f"https://{AUTH0_DOMAIN}/",
            options=verify_options
        )
        
        logger.info(f"✅ Token verified successfully for user: {payload.get('sub', 'unknown')}")
        logger.debug(f"Token payload: sub={payload.get('sub')}, email={payload.get('email')}, aud={payload.get('aud')}")
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ Auth0 token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.JWTClaimsError as e:
        logger.warning(f"⚠️ Auth0 token claims error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token claims: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError as e:
        logger.error(f"❌ Auth0 token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error validating Auth0 token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

async def get_current_auth0_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Extract and validate Auth0 user from Bearer token
    Returns user info or None if not authenticated
    """
    if not credentials:
        logger.debug("🔓 No credentials provided")
        return None
    
    try:
        logger.debug(f"🔐 Verifying Auth0 token: {credentials.credentials[:20]}...")
        payload = verify_auth0_token(credentials.credentials)
        
        # Extract user information from token payload
        user_info = {
            "sub": payload.get("sub"),  # Auth0 user ID
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified", False),
            "name": payload.get("name"),
            "nickname": payload.get("nickname"),
            "picture": payload.get("picture"),
            "permissions": payload.get("permissions", []),
            "scope": payload.get("scope", ""),
        }
        
        logger.info(f"✅ Authenticated user: {user_info.get('email', user_info.get('sub'))}")
        return user_info
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error extracting Auth0 user: {e}", exc_info=True)
        return None

async def require_auth0_user(
    user: Optional[dict] = Depends(get_current_auth0_user)
) -> dict:
    """Require authenticated Auth0 user - raises 401 if not authenticated"""
    if not user:
        logger.warning("⚠️ Authentication required but user not authenticated")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

async def require_auth0_admin(
    user: dict = Depends(require_auth0_user)
) -> dict:
    """
    Require authenticated Auth0 admin user
    Checks if user email matches allowed admin emails
    """
    user_email = user.get("email", "").lower()
    
    # Check against allowed admin emails
    allowed_emails = [settings.ALLOWED_ADMIN_EMAIL.lower()]
    if hasattr(settings, 'ALLOWED_ADMIN_EMAILS'):
        allowed_emails.extend([e.lower() for e in settings.ALLOWED_ADMIN_EMAILS])
    
    logger.debug(f"🔍 Checking admin access for: {user_email}")
    logger.debug(f"🔍 Allowed admins: {allowed_emails}")
    
    if user_email not in allowed_emails:
        logger.warning(f"🚫 Unauthorized admin access attempt by: {user_email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Add admin flag to user object
    user["is_admin"] = True
    logger.info(f"✅ Admin access granted to: {user_email}")
    return user

def check_auth0_permission(required_permission: str):
    """
    Dependency factory to check for specific Auth0 permission
    Usage: @router.get("/endpoint", dependencies=[Depends(check_auth0_permission("read:data"))])
    """
    async def permission_checker(user: dict = Depends(require_auth0_user)) -> dict:
        permissions = user.get("permissions", [])
        scope = user.get("scope", "").split()
        
        if required_permission not in permissions and required_permission not in scope:
            logger.warning(f"🚫 Permission denied: {required_permission} for user {user.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {required_permission}"
            )
        return user
    
    return permission_checker

# Helper function for backwards compatibility with existing code
async def get_current_user_compatible(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Backwards compatible wrapper that tries Auth0 first, then falls back to session cookie
    This allows gradual migration of endpoints
    """
    # Try Auth0 first
    try:
        auth0_user = await get_current_auth0_user(credentials)
        if auth0_user:
            return auth0_user
    except:
        pass
    
    # Fallback to session cookie auth (for transition period)
    # This will be removed once all endpoints are migrated to Auth0
    from app.core.security import get_current_user as get_session_user
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # Note: This requires passing the request object
    # Individual endpoints may need updating
    return None
