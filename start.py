#!/usr/bin/env python3
r"""
FastAPI Backend Startup Script
"""
import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

def check_requirements():
    """Check if all required packages are installed"""
    missing = []
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    try:
        import jwt
    except ImportError:
        missing.append("PyJWT")
    try:
        import supabase
    except ImportError:
        missing.append("supabase")
    try:
        import websockets
    except ImportError:
        missing.append("websockets")

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False

    print("✅ All requirements are installed")
    return True

def check_environment():
    """Check if environment variables are set"""
    # Check for required env vars - use flexible naming
    supabase_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    missing_vars = []
    if not supabase_url:
        missing_vars.append("SUPABASE_URL or NEXT_PUBLIC_SUPABASE_URL")
    if not supabase_key:
        missing_vars.append("SUPABASE_ANON_KEY or NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables")
        print("See the .env.example for reference")
        return False

    print("✅ Environment variables are configured")
    return True

def create_data_directory():
    """Create data directory and initialize blog-posts.json"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    blog_file = data_dir / "blog-posts.json"
    if not blog_file.exists():
        blog_file.write_text("[]")
        print("✅ Created empty blog posts file")

    print("✅ Data directory is ready")

def main():
    """Main startup function"""
    print("🚀 Starting CortejTech FastAPI Backend...")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Create data directory
    create_data_directory()

    print("=" * 50)
    print("🎉 All checks passed! Starting server...")

    # Determine port (use Render's $PORT if available)
    port = int(os.getenv("PORT", 8000))

    print(f"📍 API will be available at: http://localhost:{port} (or your Render URL)")
    print(f"📖 API documentation: http://localhost:{port}/docs")
    print(f"🔧 Admin endpoints: http://localhost:{port}/api/admin/")
    print("=" * 50)

    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True if os.getenv("ENVIRONMENT") == "development" else False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
