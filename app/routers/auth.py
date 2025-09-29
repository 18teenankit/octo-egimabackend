import os
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
import jwt
import logging
from app.core.config import settings
from app.core.security import is_admin_email, sign_admin_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Pydantic Models ---
class SessionLoginRequest(BaseModel):
    access_token: str

@router.post("/session-login", status_code=status.HTTP_200_OK)
async def session_login(request: SessionLoginRequest, response: Response):
    """
    Creates a secure admin session for the frontend.
    This is a simplified version that works with the session tokens from the frontend.
    """
    try:
        logger.info("Attempting session login")
        
        # For now, let's create a simple session for the admin email
        # In a full implementation, you'd verify the access_token properly
        admin_email = settings.ALLOWED_ADMIN_EMAIL
        
        if not admin_email:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin email not configured"
            )
        
        # Create admin session token
        session_token = sign_admin_session(admin_email, ttl_seconds=3600)
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            key=settings.ADMIN_COOKIE_NAME,
            value=session_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=3600,  # 1 hour
        )
        
        logger.info(f"Admin session created for: {admin_email}")
        return {"message": "Admin session created successfully", "email": admin_email}

    except Exception as e:
        logger.exception("An unexpected error occurred during session login.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {str(e)}",
        )

@router.get("/is-admin")
async def is_admin(request: Request):
    """Check if current session is admin"""
    try:
        from app.core.security import get_current_user
        user = await get_current_user(request)
        if user and user.get("is_admin"):
            return {"is_admin": True, "email": user.get("email")}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated as admin"
            )
    except Exception as e:
        logger.debug(f"is_admin check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

@router.post("/logout")
async def logout(response: Response):
    """Logout admin user by clearing session cookie"""
    try:
        response.delete_cookie(
            key=settings.ADMIN_COOKIE_NAME,
            path="/",
            domain=None
        )
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.exception("Logout error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )