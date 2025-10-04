"""
Auth0 Authentication Router for FastAPI Backend
Handles Auth0 token validation and admin verification
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.auth0_security import (
    get_current_auth0_user,
    require_auth0_user,
    require_auth0_admin
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_auth_info():
    """Get authentication API information and available endpoints"""
    return {
        "message": "Auth0 Authentication API",
        "version": "2.0",
        "auth_provider": "Auth0",
        "endpoints": [
            "GET /me - Get current authenticated user info",
            "GET /verify - Verify Auth0 token", 
            "GET /is-admin - Check if user has admin privileges"
        ],
        "note": "All authentication is handled via Auth0. Frontend should redirect to /api/auth/login for login."
    }

@router.get("/me")
async def get_current_user_info(user: dict = Depends(require_auth0_user)):
    """
    Get current authenticated user information from Auth0 token
    Requires valid Auth0 Bearer token in Authorization header
    """
    return {
        "user": {
            "id": user.get("sub"),
            "email": user.get("email"),
            "email_verified": user.get("email_verified"),
            "name": user.get("name"),
            "nickname": user.get("nickname"),
            "picture": user.get("picture"),
        },
        "authenticated": True
    }

@router.get("/verify")
async def verify_token(user: dict = Depends(require_auth0_user)):
    """
    Verify Auth0 access token
    Returns success if token is valid
    """
    return {
        "valid": True,
        "user_id": user.get("sub"),
        "email": user.get("email")
    }

@router.get("/is-admin")
async def check_admin_status(user: dict = Depends(require_auth0_admin)):
    """
    Check if current user has admin privileges
    Requires valid Auth0 token AND email must be in allowed admin list
    """
    return {
        "is_admin": True,
        "email": user.get("email"),
        "user_id": user.get("sub")
    }

# Legacy endpoint for backwards compatibility - returns Auth0 user if available
@router.get("/session")
async def get_session(user: dict = Depends(get_current_auth0_user)):
    """
    Legacy session endpoint for backwards compatibility
    Now returns Auth0 user information if authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "authenticated": True,
        "user": {
            "email": user.get("email"),
            "name": user.get("name"),
            "picture": user.get("picture")
        }
    }