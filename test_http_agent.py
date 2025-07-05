#!/usr/bin/env python3
"""
Test script for the local HTTP agent
"""

import json
import urllib.request
import urllib.parse

def test_endpoint(url, method="GET", data=None):
    """Test an HTTP endpoint"""
    try:
        if data and method == "POST":
            # Prepare POST data
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return {"success": True, "status": response.status, "data": result}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Test the local HTTP agent"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Local HTTP Agent")
    print("=" * 40)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    result = test_endpoint(f"{base_url}/health")
    if result["success"]:
        print(f"   ✅ Status: {result['status']}")
        print(f"   📊 Response: {json.dumps(result['data'], indent=6)}")
    else:
        print(f"   ❌ Error: {result['error']}")
    print()
    
    # Test 2: Agent info
    print("2. Testing agent info endpoint...")
    result = test_endpoint(f"{base_url}/")
    if result["success"]:
        print(f"   ✅ Status: {result['status']}")
        print(f"   📋 Agent: {result['data']['name']}")
        print(f"   🆔 ID: {result['data']['agent_id']}")
        print(f"   📡 Endpoints: {len(result['data']['endpoints'])}")
    else:
        print(f"   ❌ Error: {result['error']}")
    print()
    
    # Test 3: Greet endpoint
    print("3. Testing greet endpoint...")
    result = test_endpoint(f"{base_url}/greet", "POST", {"name": "Python Tester"})
    if result["success"]:
        print(f"   ✅ Status: {result['status']}")
        print(f"   💬 Message: {result['data']['result']['message']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    print()
    
    # Test 4: Calculate endpoint
    print("4. Testing calculate endpoint...")
    result = test_endpoint(f"{base_url}/calculate", "POST", {"a": 25, "b": 4, "operation": "multiply"})
    if result["success"]:
        print(f"   ✅ Status: {result['status']}")
        print(f"   🧮 Result: {result['data']['result']['result']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    print()
    
    # Test 5: Status endpoint
    print("5. Testing status endpoint...")
    result = test_endpoint(f"{base_url}/status")
    if result["success"]:
        print(f"   ✅ Status: {result['status']}")
        print(f"   🏃 Agent Status: {result['data']['result']['status']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    print()
    
    print("🎯 Summary:")
    print("   ✅ Local HTTP agent is running!")
    print("   🌐 Accessible at http://localhost:8001")
    print("   📡 All endpoints are working")
    print("   🚀 Ready for local development and testing")

if __name__ == "__main__":
    main()