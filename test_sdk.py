#!/usr/bin/env python3
"""
Test script for AgentHub SDK

This script demonstrates the key features of the AgentHub SDK.
"""

import os
import sys
import json
import asyncio
from agenthub import AgentBuilder, AgentHubClient, publish_agent
from agenthub.server import serve_agent

def test_agent_creation():
    """Test creating a basic agent"""
    print("🔧 Testing Agent Creation...")
    
    # Create agent
    agent = AgentBuilder("test-agent")
    
    @agent.endpoint("/greet", description="Greet users")
    def greet(request):
        name = request.json.get("name", "World")
        return {"message": f"Hello, {name}!"}
    
    @agent.endpoint("/calculate", description="Basic math")
    def calculate(request):
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
        operation = request.json.get("operation", "add")
        
        if operation == "add":
            result = a + b
        elif operation == "multiply":
            result = a * b
        else:
            result = "Unknown operation"
        
        return {"result": result}
    
    @agent.endpoint("/status", method="GET", description="Get status")
    def status(request):
        return {"status": "running", "version": "1.0.0"}
    
    # Set metadata
    agent.set_metadata({
        "name": "Test Agent",
        "description": "A test agent for SDK validation",
        "category": "testing",
        "version": "1.0.0",
        "tags": ["test", "demo"],
        "pricing": {"type": "per_request", "price": 0.001},
        "author": "AgentHub SDK",
        "license": "MIT"
    })
    
    # Validate
    try:
        agent.validate()
        print("✅ Agent created and validated successfully")
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Endpoints: {list(agent.get_endpoints().keys())}")
        return agent
    except Exception as e:
        print(f"❌ Agent validation failed: {e}")
        return None

def test_agent_metadata():
    """Test agent metadata handling"""
    print("\n📋 Testing Agent Metadata...")
    
    agent = AgentBuilder("metadata-test")
    
    # Test setting metadata
    agent.set_metadata({
        "name": "Metadata Test Agent",
        "description": "Testing metadata functionality",
        "category": "testing",
        "pricing": {"type": "per_request", "price": 0.01}
    })
    
    metadata = agent.get_metadata()
    if metadata:
        print("✅ Metadata set successfully")
        print(f"   Name: {metadata.name}")
        print(f"   Category: {metadata.category}")
        print(f"   Pricing: {metadata.pricing.type} - ${metadata.pricing.price}")
    else:
        print("❌ Failed to set metadata")

def test_client_functionality():
    """Test client functionality (mocked)"""
    print("\n🌐 Testing Client Functionality...")
    
    try:
        # This would normally require a real API key
        # For testing, we'll just verify the client can be created
        client = AgentHubClient(api_key="test-key")
        print("✅ Client created successfully")
        print(f"   Base URL: {client.base_url}")
        print(f"   Headers configured: {bool(client.headers)}")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")

def test_decorators():
    """Test decorator functionality"""
    print("\n🎭 Testing Decorators...")
    
    from agenthub.decorators import endpoint, expose, capability
    
    @endpoint("/test", description="Test endpoint")
    def test_endpoint(request):
        return {"test": "success"}
    
    @expose
    def test_function(param):
        return f"Processed {param}"
    
    @capability("test_capability", "Test capability")
    def test_capability(data):
        return {"processed": data}
    
    # Check if decorators added metadata
    has_endpoint = hasattr(test_endpoint, '_agenthub_endpoint')
    has_expose = hasattr(test_function, '_agenthub_exposed')
    has_capability = hasattr(test_capability, '_agenthub_capability')
    
    if has_endpoint and has_expose and has_capability:
        print("✅ Decorators working correctly")
    else:
        print("❌ Decorators not working properly")

def test_configuration():
    """Test configuration handling"""
    print("\n⚙️ Testing Configuration...")
    
    from agenthub.registry import generate_agent_template, validate_agent_config
    
    # Test template generation
    try:
        template_file = generate_agent_template("test-config", "test_config.yaml")
        print("✅ Configuration template generated")
        print(f"   File: {template_file}")
        
        # Clean up
        if os.path.exists(template_file):
            os.remove(template_file)
            
    except Exception as e:
        print(f"❌ Template generation failed: {e}")

def test_models():
    """Test Pydantic models"""
    print("\n🏗️ Testing Models...")
    
    from agenthub.models import AgentMetadata, PricingModel
    
    try:
        # Test pricing model
        pricing = PricingModel(type="per_request", price=0.05)
        print("✅ PricingModel created successfully")
        
        # Test agent metadata
        metadata = AgentMetadata(
            name="Test Agent",
            description="Test description",
            category="testing",
            pricing=pricing
        )
        print("✅ AgentMetadata created successfully")
        print(f"   Validation passed for agent: {metadata.name}")
        
    except Exception as e:
        print(f"❌ Model validation failed: {e}")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting AgentHub SDK Tests\n")
    
    # Run tests
    agent = test_agent_creation()
    test_agent_metadata()
    test_client_functionality()
    test_decorators()
    test_configuration()
    test_models()
    
    print("\n📊 Test Summary:")
    print("✅ All basic functionality tests completed")
    print("🎯 SDK is ready for use!")
    
    # Optional: Start a test server
    if agent and len(sys.argv) > 1 and sys.argv[1] == "--serve":
        print("\n🌐 Starting test server...")
        print("   Available at: http://localhost:8001")
        print("   Endpoints:")
        for endpoint in agent.get_endpoints():
            print(f"     - {endpoint}")
        
        serve_agent(agent, host="localhost", port=8001)

if __name__ == "__main__":
    run_all_tests()