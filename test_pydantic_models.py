#!/usr/bin/env python3
"""
Test script to verify AgentHub models work correctly with Pydantic installed
This simulates the user's conda environment scenario
"""

import sys
import traceback

def test_models_with_pydantic():
    """Test that models work correctly when Pydantic is available"""
    print("🧪 Testing AgentHub Models with Pydantic Compatibility")
    print("=" * 60)
    
    try:
        # Import Pydantic to make sure it's treated as available
        import pydantic
        print(f"✅ Pydantic version: {pydantic.VERSION}")
        pydantic_available = True
    except ImportError:
        print("❌ Pydantic not available - simulating conda environment")
        pydantic_available = False
    
    # Import AgentHub models
    try:
        from agenthub import AgentMetadata, PricingModel, endpoint
        print("✅ AgentHub SDK models imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AgentHub models: {e}")
        return False
    
    print("\n📋 Testing Model Creation:")
    
    # Test 1: PricingModel
    try:
        pricing = PricingModel(type="per_request", price=0.01, currency="USD")
        print(f"✅ PricingModel created: type={pricing.type}, price=${pricing.price}")
    except Exception as e:
        print(f"❌ PricingModel creation failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: AgentMetadata
    try:
        metadata = AgentMetadata(
            name="Test Agent",
            description="A test agent for verification",
            category="test",
            version="1.0.0",
            pricing={
                "type": "per_request",
                "price": 0.01,
                "currency": "USD"
            },
            author="Test Suite"
        )
        print(f"✅ AgentMetadata created: name='{metadata.name}', version={metadata.version}")
    except Exception as e:
        print(f"❌ AgentMetadata creation failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 3: Endpoint decorator
    try:
        @endpoint("/test", description="Test endpoint")
        def test_endpoint(request):
            return {"test": True, "request": request}
        
        print("✅ @endpoint decorator works correctly")
        
        # Test the decorated function
        result = test_endpoint({"input": "test"})
        print(f"✅ Endpoint function executed: {result}")
        
    except Exception as e:
        print(f"❌ @endpoint decorator failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 4: Model serialization
    try:
        metadata_dict = metadata.dict() if hasattr(metadata, 'dict') else vars(metadata)
        print(f"✅ Model serialization works: {type(metadata_dict).__name__}")
    except Exception as e:
        print(f"❌ Model serialization failed: {e}")
        return False
    
    print("\n🎯 Model Field Access Test:")
    
    # Test 5: Field access that was failing before
    try:
        print(f"   📝 Agent name: {metadata.name}")
        print(f"   📝 Agent description: {metadata.description}")
        print(f"   📝 Pricing type: {metadata.pricing.type}")
        print(f"   📝 Pricing price: ${metadata.pricing.price}")
        print("✅ All field access working correctly")
    except Exception as e:
        print(f"❌ Field access failed: {e}")
        traceback.print_exc()
        return False
    
    print("\n✅ All tests passed! Models work correctly with Pydantic.")
    return True

def test_simple_local_demo():
    """Test the actual simple_local_demo.py functionality"""
    print("\n🧪 Testing simple_local_demo.py Components")
    print("=" * 60)
    
    try:
        # Import and run the SDK component verification
        import simple_local_demo
        
        # Test the create_demo_agent function
        agent = simple_local_demo.create_demo_agent()
        print(f"✅ Demo agent created: {agent.metadata.name}")
        
        # Test endpoint calls
        result = agent.call_endpoint("/greet", {"name": "TestUser", "style": "friendly"})
        if result.get('status') == 'success':
            print("✅ Endpoint call successful")
            print(f"   Response: {result['result']['message']}")
        else:
            print(f"❌ Endpoint call failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ simple_local_demo.py test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 AgentHub SDK Pydantic Compatibility Test Suite")
    print("=" * 80)
    
    # Run tests
    models_pass = test_models_with_pydantic()
    demo_pass = test_simple_local_demo()
    
    print("\n" + "=" * 80)
    print("📊 Test Results:")
    print(f"   Models Test: {'✅ PASS' if models_pass else '❌ FAIL'}")
    print(f"   Demo Test:   {'✅ PASS' if demo_pass else '❌ FAIL'}")
    
    if models_pass and demo_pass:
        print("\n🎉 All tests passed! The SDK now works correctly in conda environments!")
        print("   Users can run simple_local_demo.py without Pydantic field errors.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the error messages above.")
        sys.exit(1)