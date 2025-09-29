#!/usr/bin/env python3
"""
Test script to verify CORS and host configuration
"""
import requests
import json

def test_cors():
    """Test CORS configuration"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing CORS Configuration...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test CORS preflight
    try:
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(f"{base_url}/api/content", headers=headers)
        print(f"✅ CORS preflight: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ CORS preflight failed: {e}")
    
    # Test API endpoint
    try:
        headers = {"Origin": "http://localhost:3000"}
        response = requests.get(f"{base_url}/api/content", headers=headers)
        print(f"✅ API endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ API endpoint failed: {e}")

def test_render_deployment():
    """Test Render deployment"""
    base_url = "https://cortejtech-backend.onrender.com"
    
    print("\n🌐 Testing Render Deployment...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Render health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Render health check failed: {e}")
    
    # Test CORS from frontend domain
    try:
        headers = {
            "Origin": "https://your-frontend-domain.com",  # Replace with actual domain
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(f"{base_url}/api/content", headers=headers, timeout=10)
        print(f"✅ Render CORS preflight: {response.status_code}")
    except Exception as e:
        print(f"❌ Render CORS preflight failed: {e}")

if __name__ == "__main__":
    print("🚀 CortejTech Backend CORS Test")
    print("Make sure your backend is running locally (python start.py)")
    print()
    
    # Test local server
    test_cors()
    
    # Test Render deployment
    test_render_deployment()
    
    print("\n✨ Testing complete!")