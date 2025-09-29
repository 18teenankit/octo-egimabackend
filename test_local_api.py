#!/usr/bin/env python3
"""
Local API Test Script
Tests the FastAPI backend endpoints that had issues in the remote deployment
"""

import requests
import json
from typing import Dict, Any

# Local API base URL
API_BASE = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code == expected_status,
        }
        
        # Try to parse JSON response
        try:
            result["response"] = response.json()
            result["has_data"] = bool(result["response"])
        except:
            result["response"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
            result["has_data"] = bool(response.text)
            
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "error": str(e),
            "success": False
        }

def main():
    print("🔍 CortejTech Local API Test Results")
    print("=" * 50)
    
    # Core endpoints that should work
    core_endpoints = [
        ("GET", "/"),
        ("GET", "/health"),
        ("GET", "/docs"),
        ("GET", "/openapi.json"),
    ]
    
    # Previously problematic endpoints
    problem_endpoints = [
        ("GET", "/api/content"),      # Was 405 - now should work
        ("GET", "/api/content/about"), # Was working
        ("GET", "/api/services"),     # Was 405 - should redirect or work
        ("GET", "/api/services/"),    # Was working
        ("GET", "/api/team"),         # Was 405 - should redirect or work  
        ("GET", "/api/team/"),        # Was working
        ("GET", "/api/auth"),         # Was 405 - now should work
        ("GET", "/api/auth/"),        # Now should work
        ("GET", "/api/admin"),        # Was 405 - now should work
        ("GET", "/api/admin/"),       # Now should work
    ]
    
    # Data endpoints 
    data_endpoints = [
        ("GET", "/api/portfolio/"),
        ("GET", "/api/faq/"),
        ("GET", "/api/testimonials/"),
        ("GET", "/api/placeholder/300/200"),
    ]
    
    all_tests = [
        ("Core System Endpoints", core_endpoints),
        ("Previously Problematic Endpoints", problem_endpoints), 
        ("Data Endpoints", data_endpoints)
    ]
    
    for section_name, endpoints in all_tests:
        print(f"\n📋 {section_name}")
        print("-" * 40)
        
        for method, endpoint in endpoints:
            result = test_endpoint(method, endpoint)
            
            if result.get("success"):
                status_icon = "✅"
                status_text = f"{result['status_code']}"
            else:
                status_icon = "❌" 
                status_text = f"{result.get('status_code', 'ERROR')}"
                
            # Check if endpoint has data
            data_info = ""
            if result.get("has_data"):
                if isinstance(result.get("response"), dict):
                    if any(key in result["response"] for key in ["message", "status", "endpoints"]):
                        data_info = " (Info)"
                    elif any(isinstance(result["response"].get(key), list) for key in result["response"]):
                        list_keys = [k for k, v in result["response"].items() if isinstance(v, list)]
                        if list_keys:
                            list_len = len(result["response"][list_keys[0]])
                            data_info = f" ({list_len} items)" if list_len > 0 else " (Empty)"
                        else:
                            data_info = " (Has Data)"
                    else:
                        data_info = " (Has Data)"
                elif isinstance(result.get("response"), list):
                    data_info = f" ({len(result['response'])} items)" if result["response"] else " (Empty)"
                else:
                    data_info = " (Has Data)"
            
            print(f"{status_icon} {method} {endpoint} → {status_text}{data_info}")
            
            # Show errors
            if not result.get("success") and result.get("error"):
                print(f"   Error: {result['error']}")
            elif not result.get("success") and result.get("response"):
                resp_preview = str(result["response"])[:100]
                print(f"   Response: {resp_preview}...")
    
    print(f"\n🎯 Local API Test Complete!")
    print(f"Backend running at: {API_BASE}")
    print("Check the results above to verify all endpoints are working correctly.")

if __name__ == "__main__":
    main()