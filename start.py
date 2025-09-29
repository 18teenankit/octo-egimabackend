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
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import supabase
        import websockets
        print("✅ All requirements are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set"""
    required_vars = [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        return False
    
    print("✅ Environment variables are configured")
    return True

def create_data_directory():
    """Create data directory for blog posts"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create empty blog posts file if it doesn't exist
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
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🔧 Admin endpoints: http://localhost:8000/api/admin/")
    print("=" * 50)
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
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