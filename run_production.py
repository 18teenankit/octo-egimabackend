#!/usr/bin/env python3
"""
Production deployment script for CortejTech Backend
Validates environment and starts the server with production settings
"""
import os
import sys
import logging
from app.core.config import settings

def validate_production_environment():
    """Validate that all required environment variables are set for production"""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'JWT_SECRET_KEY',
        'ADMIN_SESSION_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Check for weak secrets
    jwt_secret = os.getenv('JWT_SECRET_KEY', '')
    if len(jwt_secret) < 32:
        print("❌ JWT_SECRET_KEY must be at least 32 characters long")
        sys.exit(1)
    
    admin_secret = os.getenv('ADMIN_SESSION_SECRET', '')
    if len(admin_secret) < 32:
        print("❌ ADMIN_SESSION_SECRET must be at least 32 characters long")
        sys.exit(1)
    
    print("✅ All required environment variables are set")

def main():
    """Main production startup function"""
    print("🚀 Starting CortejTech Backend in Production Mode...")
    print("=" * 60)
    
    # Validate environment
    validate_production_environment()
    
    # Set production environment
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DEBUG'] = 'false'
    
    print("✅ Environment validation passed")
    print("🔒 Security settings applied")
    print("=" * 60)
    
    # Import and start server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            workers=4,
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()