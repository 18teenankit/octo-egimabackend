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

# Import routers
from app.routers import auth, admin, contact, content, services, team, portfolio, faq, testimonials
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

# Dev-friendly CORS: when DEBUG, install a permissive middleware to handle preflight
class DevCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        origin = request.headers.get("origin", "*")
        if request.method == "OPTIONS":
            # Respond to preflight without strict checks (Next.js proxy may omit some headers)
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*") or "*",
                "Vary": "Origin",
            })
        response = await call_next(request)
        # Set CORS headers on normal responses
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers.setdefault("Vary", "Origin")
        return response

"""
Middleware order note (Starlette): last added runs first on requests.
We want CORS to be the outermost middleware so it can handle preflights and set headers.
TrustedHost middleware is configured more permissively to avoid "Invalid Host Header" errors.
"""

# Inner middlewares first
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

# Configure CORS - this will be the outermost middleware
cors_origins = list(settings.ALLOWED_ORIGINS)

# Add Render domain if not already present
render_url = "https://cortejtech-backend.onrender.com"
if render_url not in cors_origins:
    cors_origins.append(render_url)

# In development or when testing, allow additional origins
if settings.DEBUG or settings.ENVIRONMENT == "development":
    app.add_middleware(DevCORSMiddleware)
else:
    # Production CORS setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins + ["*"] if settings.ENVIRONMENT == "testing" else cors_origins,
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
# Mount auth routes under /api/auth for consistency with admin client and main_admin
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(team.router, prefix="/api/team", tags=["team"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(faq.router, prefix="/api/faq", tags=["faq"])
app.include_router(testimonials.router, prefix="/api/testimonials", tags=["testimonials"])
app.include_router(contacts_router, prefix="/api", tags=["contacts-compat"])  # /api/contacts

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