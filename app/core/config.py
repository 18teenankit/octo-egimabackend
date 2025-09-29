from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices
from typing import List
import os
from dotenv import load_dotenv

# Ensure .env is loaded even if parent process didn't set it
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Database (support both SUPABASE_* and NEXT_PUBLIC_SUPABASE_* env names)
    SUPABASE_URL: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL"),
    )
    SUPABASE_ANON_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_ANON_KEY", "NEXT_PUBLIC_SUPABASE_ANON_KEY"),
    )
    SUPABASE_SERVICE_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
    )
    # Keep the NEXT_PUBLIC_* as optional to allow direct reading if needed
    NEXT_PUBLIC_SUPABASE_URL: str = ""
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    # Optional Supabase JWT secret for verifying user JWTs locally.
    SUPABASE_JWT_SECRET: str = Field(default="")
    
    # Authentication
    JWT_SECRET_KEY: str = Field(default="dev-fallback-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin
    ALLOWED_ADMIN_EMAIL: str = Field(default="giriankit595@outlook.com")
    # Comma-separated list of additional admin emails
    ALLOWED_ADMIN_EMAILS: List[str] = (
        [e.strip().lower() for e in os.getenv("ALLOWED_ADMIN_EMAILS", "giriankit595@outlook.com,info@cortejtech.com").split(",") if e.strip()]
    )
    
    # reCAPTCHA
    RECAPTCHA_SECRET_KEY: str = Field(default="")
    NEXT_PUBLIC_RECAPTCHA_SITE_KEY: str = Field(default="")
    
    # Telegram not used (explicitly disabled)
    TELEGRAM_BOT_TOKEN: str = Field(default="", frozen=True)
    TELEGRAM_CHAT_ID: str = Field(default="", frozen=True)
    
    # CORS
    ALLOWED_ORIGINS: List[str] = (
        os.getenv("ALLOWED_ORIGINS", "")
        .split(",")
        if os.getenv("ALLOWED_ORIGINS")
        else [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",  # allow dev server fallback port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001", 
            "http://127.0.0.1:3002",
            "https://cortejtech.com",
            "https://www.cortejtech.com",
            "https://cortejtech.in",
            "https://www.cortejtech.in",
            "https://cortejtech-backend.onrender.com",  # Render backend URL
            # Add your frontend domains here
            "https://your-frontend-domain.com",  # Replace with actual frontend domain
        ]
    )
    
    ALLOWED_HOSTS: List[str] = (
        os.getenv("ALLOWED_HOSTS", "").split(",")
        if os.getenv("ALLOWED_HOSTS")
        else [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",  # Important for Docker/Render
            "cortejtech.com",
            "www.cortejtech.com",
            "cortejtech.in",
            "www.cortejtech.in",
            "cortejtech-backend.onrender.com",  # Render domain
            "*.onrender.com",  # Allow any Render subdomain
        ]
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Redis (for caching and rate limiting)
    REDIS_URL: str = Field(default="redis://localhost:6379")
    
    # Environment
    ENVIRONMENT: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = Field(default=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on"))
    # Admin auth cookie name
    ADMIN_COOKIE_NAME: str = Field(default="admin_session")
    # Shared HMAC secret for admin session cookie (must match frontend ADMIN_SESSION_SECRET)
    ADMIN_SESSION_SECRET: str = Field(default="")

    # Email (Resend) configuration
    RESEND_API_KEY: str = Field(default="")
    EMAIL_FROM: str = Field(default="CortejTech <noreply@cortejtech.com>")
    NOTIFY_RECIPIENTS: str = "info@cortejtech.com,giriankit595@outlook.com"

    # Admin App base URL (used for auth redirects)
    # Prefer NEXT_PUBLIC_ADMIN_BASE_URL when present, fallback to localhost:3001 in dev
    ADMIN_BASE_URL: str = Field(
        default=os.getenv("NEXT_PUBLIC_ADMIN_BASE_URL", "http://localhost:3001")
    )

    # Auth behavior: whether to allow creating a new Supabase user via OTP login
    # If false, magic link will only be sent to pre-existing users in Supabase Auth
    ALLOW_NEW_AUTH_USERS: bool = Field(default=False)
    
    def model_post_init(self, __context) -> None:
        # Fallback: map NEXT_PUBLIC_* vars if primary fields are empty
        self._apply_fallback_mappings()
        
        # Validate critical settings in production
        if self.ENVIRONMENT == "production":
            self._validate_production_settings()
    
    def _apply_fallback_mappings(self):
        """Apply fallback mappings for environment variables"""
        if not self.SUPABASE_URL and self.NEXT_PUBLIC_SUPABASE_URL:
            self.SUPABASE_URL = self.NEXT_PUBLIC_SUPABASE_URL
        if not self.SUPABASE_ANON_KEY and self.NEXT_PUBLIC_SUPABASE_ANON_KEY:
            self.SUPABASE_ANON_KEY = self.NEXT_PUBLIC_SUPABASE_ANON_KEY
        if not self.SUPABASE_SERVICE_KEY and self.SUPABASE_SERVICE_ROLE_KEY:
            self.SUPABASE_SERVICE_KEY = self.SUPABASE_SERVICE_ROLE_KEY
    
    def _validate_production_settings(self):
        """Validate critical settings for production environment"""
        weak_secrets = ["dev-fallback-secret-change-in-production", "your-secret-key-change-in-production", "dev-secret-change"]
        
        if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY in weak_secrets:
            raise ValueError("JWT_SECRET_KEY must be set to a strong secret in production")
        if not self.SUPABASE_URL or not self.SUPABASE_ANON_KEY:
            raise ValueError("Supabase configuration is required")
        if self.DEBUG:
            raise ValueError("DEBUG must be False in production")
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        if not self.ADMIN_SESSION_SECRET or len(self.ADMIN_SESSION_SECRET) < 32:
            raise ValueError("ADMIN_SESSION_SECRET must be at least 32 characters long in production")

    @property
    def AUTH_CALLBACK_URL(self) -> str:
        base = (self.ADMIN_BASE_URL or "").rstrip("/")
        return f"{base}/auth/callback"
    
settings = Settings()