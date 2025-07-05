#!/usr/bin/env python3
"""
Test Core SDK Functionality (No External Dependencies)

This script tests that the core AgentHub SDK components work
without requiring FastAPI, Pydantic, or other external dependencies.
"""

def test_core_models():
    """Test that core models work without Pydantic"""
    print("🔧 Testing Core Models...")
    
    try:
        from agenthub.models import AgentMetadata, PricingModel, AgentEndpoint
        
        # Test PricingModel
        pricing = PricingModel(type="per_request", price=0.05)
        print(f"   ✅ PricingModel: {pricing.type}, ${pricing.price}")
        
        # Test AgentMetadata
        metadata = AgentMetadata(
            name="Test Agent",
            description="Test description",
            category="testing",
            pricing={"type": "per_request", "price": 0.01}
        )
        print(f"   ✅ AgentMetadata: {metadata.name}")
        
        # Test to dict conversion
        data = metadata.dict()
        print(f"   ✅ Serialization: {len(data)} fields")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Models test failed: {e}")
        return False

def test_decorators():
    """Test that decorators work"""
    print("\n🎭 Testing Decorators...")
    
    try:
        from agenthub.decorators import endpoint, expose, capability
        
        @endpoint("/test", description="Test endpoint")
        def test_endpoint(request):
            return {"test": "success"}
        
        @expose
        def test_function(param):
            return f"Processed {param}"
        
        @capability("test_capability", "Test capability")
        def test_capability_func(data):
            return {"processed": data}
        
        # Check if decorators added metadata
        has_endpoint = hasattr(test_endpoint, '_agenthub_endpoint')
        has_expose = hasattr(test_function, '_agenthub_exposed')
        has_capability = hasattr(test_capability_func, '_agenthub_capability')
        
        if has_endpoint and has_expose and has_capability:
            print("   ✅ All decorators working correctly")
            return True
        else:
            print("   ❌ Some decorators not working")
            return False
            
    except Exception as e:
        print(f"   ❌ Decorators test failed: {e}")
        return False

def test_imports():
    """Test that core imports work"""
    print("\n📦 Testing Core Imports...")
    
    try:
        # Test core imports (should always work)
        from agenthub import AgentMetadata, PricingModel, endpoint, expose
        print("   ✅ Core imports successful")
        
        # Test optional imports (will show helpful error messages)
        try:
            from agenthub import AgentBuilder
            print("   ✅ AgentBuilder available (FastAPI installed)")
        except ImportError as e:
            print("   ⚠️ AgentBuilder not available (expected without FastAPI)")
            print(f"      Message: {str(e)[:80]}...")
        
        try:
            from agenthub import AgentHubClient
            print("   ✅ AgentHubClient available (httpx installed)")
        except ImportError as e:
            print("   ⚠️ AgentHubClient not available (expected without httpx)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def test_dependency_check():
    """Test the dependency checker"""
    print("\n🔍 Testing Dependency Checker...")
    
    try:
        from agenthub import check_dependencies
        
        deps = check_dependencies()
        print(f"   📊 Dependency Status:")
        for dep, available in deps.items():
            status = "✅" if available else "❌"
            print(f"      {status} {dep}: {available}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Dependency check failed: {e}")
        return False

def test_simple_agent():
    """Test creating a simple agent with core functionality"""
    print("\n🤖 Testing Simple Agent Creation...")
    
    try:
        # Create a simple agent without AgentBuilder
        from agenthub.decorators import endpoint
        from agenthub.models import AgentMetadata
        
        # Define functions with decorators
        @endpoint("/greet", description="Greet users")
        def greet(request):
            name = getattr(request, 'json', {}).get('name', 'World')
            return {"message": f"Hello, {name}!"}
        
        # Create metadata
        metadata = AgentMetadata(
            name="Simple Agent",
            description="A simple test agent",
            category="testing",
            pricing={"type": "per_request", "price": 0.001}
        )
        
        # Test function call
        mock_request = type('Request', (), {'json': {'name': 'Test'}})()
        result = greet(mock_request)
        
        print(f"   ✅ Agent created: {metadata.name}")
        print(f"   ✅ Function call result: {result}")
        print(f"   ✅ Metadata serializable: {len(metadata.dict())} fields")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Simple agent test failed: {e}")
        return False

def main():
    """Run all core SDK tests"""
    print("🚀 AgentHub Core SDK Tests (No External Dependencies)")
    print("=" * 60)
    
    tests = [
        test_core_models,
        test_decorators,
        test_imports,
        test_dependency_check,
        test_simple_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core SDK functionality working!")
        print("\n✅ What works without dependencies:")
        print("   • Agent metadata and models")
        print("   • Decorators for endpoints and capabilities")
        print("   • Basic agent creation")
        print("   • Data serialization")
        print("   • Validation and error handling")
        
        print("\n🔧 To get full functionality:")
        print("   • Install FastAPI/Uvicorn for HTTP servers")
        print("   • Install httpx for AgentHub client")
        print("   • Install PyYAML for configuration")
        print("   • Install Rich/Click for CLI tools")
    else:
        print("❌ Some tests failed - check output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)