from app.core import monkeypatches  # noqa: F401  (ensure patches loaded early)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

# Import routers (auth router enabled for admin session management)
from app.routers import admin, contact, content, services, team, portfolio, faq, testimonials, auth
from app.routers.contact import admin_compat_router as contacts_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware
from app.core.database import init_db
from app.core.config import settings
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image, ImageDraw
from fastapi import Response

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    ...

app = FastAPI(
    title="CortejTech API",
    description="High-performance FastAPI backend for CortejTech admin dashboard and website",
    version="1.0.0",
    lifespan=lifespan
)
# Explicit OPTIONS handler to satisfy CORS preflight
@app.options("/{full_path:path}")
async def any_options(full_path: str):
    return Response(status_code=200)

"""
Middleware order note (Starlette): last added runs first on requests.
We want CORS to be the outermost middleware so it can handle preflights and set headers.
TrustedHost middleware is configured to work with separate hosting environments.
"""

# Inner middlewares first
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

# Configure CORS - this will be the outermost middleware
cors_origins = list(settings.ALLOWED_ORIGINS)

# In development or when testing, use permissive CORS with explicit origins
if settings.DEBUG or settings.ENVIRONMENT == "development":
    # Development: use explicit origin list but be more lenient
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,  # Explicit list, no wildcards
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    # Production CORS setup with strict origin checking
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,  # Only explicitly allowed origins
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# TrustedHost middleware - more permissive configuration to avoid host header issues
trusted_hosts = settings.ALLOWED_HOSTS.copy()
# Add Render domains
render_hosts = [
    "cortejtech-backend.onrender.com",
    "*.onrender.com",  # Allow any onrender.com subdomain
]
for host in render_hosts:
    if host not in trusted_hosts:
        trusted_hosts.append(host)

# Add TrustedHost middleware only if we have specific hosts to trust
# In development, we'll be more permissive
if not settings.DEBUG and trusted_hosts:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts + ["*"] if settings.ENVIRONMENT == "testing" else trusted_hosts
    )

# Include routers
# NOTE: Auth router provides session-login and is-admin endpoints for admin dashboard
# The admin dashboard uses Auth0 SDK routes at /api/auth/[...auth0] for Auth0 flows
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(team.router, prefix="/api/team", tags=["team"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(faq.router, prefix="/api/faq", tags=["faq"])
app.include_router(testimonials.router, prefix="/api/testimonials", tags=["testimonials"])
app.include_router(contacts_router, prefix="/api", tags=["contacts-compat"])  # /api/contacts

# Add base route handlers for endpoints without trailing slashes (fix 405 errors)
@app.get("/api/content")
async def api_content_redirect():
    """Redirect /api/content to /api/content/ (no trailing slash handler)"""
    return {
        "message": "Content API",
        "endpoints": [
            "/api/content/about - Get about page content",
            "/api/content/services - Get services content", 
            "/api/content/team - Get team content",
            "/api/content/portfolio - Get portfolio content",
            "/api/content/faq - Get FAQ content",
            "/api/content/testimonials - Get testimonials content"
        ]
    }

@app.get("/api/auth")  
async def api_auth_redirect():
    """Info endpoint - Auth0 handles authentication in the admin dashboard"""
    return {
        "message": "Authentication is handled by Auth0 in the admin dashboard",
        "note": "This backend does not provide authentication endpoints",
        "admin_auth": "Use Auth0 login at admin dashboard /api/auth/login"
    }

@app.get("/api/admin")
async def api_admin_redirect():
    """Redirect /api/admin to /api/admin/ (no trailing slash handler)"""
    return {
        "message": "Admin API", 
        "endpoints": [
            "GET /api/admin/dashboard/stats - Get dashboard statistics",
            "GET /api/admin/contacts - Get all contact messages",
            "PUT /api/admin/contacts/{contact_id} - Update contact message", 
            "DELETE /api/admin/contacts/{contact_id} - Delete contact message"
        ]
    }

@app.get("/api/services")
async def api_services_redirect():
    """Redirect /api/services to /api/services/ (no trailing slash handler)"""
    from app.routers.services import get_services
    return await get_services()

@app.get("/api/team") 
async def api_team_redirect():
    """Redirect /api/team to /api/team/ (no trailing slash handler)"""
    from app.routers.team import get_team_members
    return await get_team_members()

# TEMP: Admin auth disabled; explicit is-admin and session-login endpoints removed.

# Debug: list routes at startup to verify registrations
try:
    logger.info("Registered routes:")
    for r in app.routes:
        try:
            methods = getattr(r, 'methods', None)
            logger.info("%s -> %s", getattr(r, 'path', str(r)), sorted(list(methods)) if methods else None)
        except Exception:
            pass
except Exception:
    pass

# Global exception handler (ensure JSON on unexpected errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global fallback exception handler.

    Logs the exception with traceback and returns a generic 500 response so
    implementation details are not leaked to clients.
    """
    logger.exception("Unhandled exception processing %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/")
async def root():
    return {"message": "CortejTech FastAPI Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/placeholder/{width}/{height}")
async def placeholder(width: int, height: int):
    # Generate a simple gray placeholder PNG dynamically
    w = max(1, min(width, 2000))
    h = max(1, min(height, 2000))
    img = Image.new("RGB", (w, h), color=(28, 28, 28))
    draw = ImageDraw.Draw(img)
    text = f"{w}x{h}"
    # Basic centered text
    try:
        # Use textbbox for newer Pillow versions, fallback to textsize for older ones
        try:
            bbox = draw.textbbox((0, 0), text)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            tw, th = draw.textsize(text)
        draw.text(((w - tw) / 2, (h - th) / 2), text, fill=(200, 200, 200))
    except Exception:
        pass
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
    # Configure basic logging if not already configured by parent process
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    
    # Use PORT environment variable (for Render) or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Important: bind to all interfaces for Render
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        workers=1 if os.getenv("ENVIRONMENT") == "development" else 4
    )