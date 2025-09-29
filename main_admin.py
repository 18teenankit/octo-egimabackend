from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routers import auth, admin
from app.routers.contact import admin_compat_router as contacts_router
from app.routers import contact as contact_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware
from app.core.database import init_db
from app.core.config import settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="CortejTech Admin API",
    description="Admin-only FastAPI backend for managing main site content",
    version="1.0.0",
    lifespan=lifespan,
)

# Security & rate limit
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS & hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Admin-only routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(contacts_router, prefix="/api", tags=["contacts-compat"])  # /api/contacts
app.include_router(contact_router.router, prefix="/api/contact", tags=["contact"])  # /api/contact/messages

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/")
async def root():
    return {"message": "CortejTech Admin API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_admin:app",
        host="0.0.0.0",
        port=int(os.getenv("ADMIN_API_PORT", "8001")),
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        workers=1 if os.getenv("ENVIRONMENT") == "development" else 2,
    )
