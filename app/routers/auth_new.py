import os
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
import jwt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
ALLOWED_EMAIL = "giriankit595@outlook.com"
SESSION_COOKIE_NAME = "admin_session"

if not SUPABASE_JWT_SECRET:
    raise RuntimeError("SUPABASE_JWT_SECRET environment variable is not set.")

# --- Pydantic Models ---
class SessionLoginRequest(BaseModel):
    token: str

# --- APIRouter ---
router = APIRouter()

@router.post("/auth/session-login", status_code=status.HTTP_200_OK)
async def session_login(request: SessionLoginRequest, response: Response):
    """
    Verifies a Supabase JWT and creates a secure, HTTP-only session cookie
    if the user is the allowed admin.
    """
    try:
        logger.info("Attempting to decode JWT.")
        payload = jwt.decode(
            request.token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        logger.info(f"JWT decoded successfully for subject: {payload.get('sub')}")

        user_email = payload.get("email")
        if not user_email or user_email.lower() != ALLOWED_EMAIL.lower():
            logger.warning(f"Login attempt from unauthorized email: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this application.",
            )

        logger.info(f"Authorized email verified: {user_email}")

        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=request.token,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/",
            max_age=60 * 60 * 24,  # 1 day
        )
        logger.info("Admin session cookie set successfully.")
        return {"message": "Admin session created successfully."}

    except jwt.ExpiredSignatureError:
        logger.error("JWT has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session token has expired."
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT provided: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token."
        )
    except Exception as e:
        logger.exception("An unexpected error occurred during session login.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred.",
        )

async def verify_admin_session(request: Request):
    """
    Dependency that verifies the admin session cookie.
    """
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt.decode(
            session_token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        if payload.get("email", "").lower() != ALLOWED_EMAIL.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin credentials.",
            )
        return True
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session has expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token."
        )

@router.get("/auth/is-admin")
async def is_admin(is_admin: bool = Depends(verify_admin_session)):
    """A protected endpoint to check if the user is an admin."""
    return {"is_admin": is_admin}
