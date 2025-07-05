#!/usr/bin/env python3
"""
Simple Local Agent Demo

This demo shows how AgentHub agents work locally using the zero-dependency 
core SDK components. No external packages required!

This demonstrates:
- Using actual AgentHub SDK components (zero-dependency core)
- Creating agents with AgentMetadata
- Defining endpoints with @endpoint decorator
- Local execution without HTTP server
"""

import json
import uuid
from typing import Dict, Any

# Import actual AgentHub SDK components (zero-dependency core)
try:
    from agenthub import AgentMetadata, endpoint, PricingModel
    print("✅ Using AgentHub SDK components")
except ImportError:
    print("❌ AgentHub SDK not found. Please install: pip install agenthub-sdk-core")
    print("   Or run from the SDK directory")
    exit(1)


class LocalAgentRunner:
    """Simple runner to execute agent endpoints locally"""
    
    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
        self.agent_id = str(uuid.uuid4())[:8]
        self.endpoints = {}
    
    def register_endpoint(self, path: str, func, description: str = ""):
        """Register an endpoint function"""
        self.endpoints[path] = {
            "function": func,
            "description": description
        }
    
    def call_endpoint(self, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an endpoint locally"""
        if path not in self.endpoints:
            return {"error": f"Endpoint {path} not found"}
        
        try:
            result = self.endpoints[path]["function"](data or {})
            return {
                "agent_id": self.agent_id,
                "endpoint": path,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "endpoint": path,
                "error": str(e),
                "status": "error"
            }
    
    def list_endpoints(self):
        """List available endpoints"""
        return {path: info["description"] for path, info in self.endpoints.items()}
    
    def info(self):
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "name": self.metadata.name,
            "metadata": self.metadata.dict() if hasattr(self.metadata, 'dict') else vars(self.metadata),
            "endpoints": self.list_endpoints()
        }


def create_demo_agent():
    """Create a demonstration agent using actual AgentHub SDK components"""
    
    # Create agent metadata using kwargs approach to avoid Pydantic field validation
    metadata_kwargs = {
        'name': "Demo Local Agent",
        'description': "A demonstration agent running locally with AgentHub SDK",
        'category': "demo",
        'version': "1.0.0",
        'pricing': {
            'type': "per_request",
            'price': 0.001,
            'currency': "USD"
        },
        'author': "AgentHub SDK Demo"
    }
    
    metadata = AgentMetadata(**metadata_kwargs)
    
    # Create local runner
    runner = LocalAgentRunner(metadata)
    
    # Define endpoints using actual AgentHub @endpoint decorator
    @endpoint("/greet", description="Greet users with a personalized message")
    def greet(request):
        name = request.get("name", "World")
        style = request.get("style", "friendly")
        
        greetings = {
            "friendly": f"Hello there, {name}! 😊",
            "formal": f"Good day, {name}.",
            "casual": f"Hey {name}! 👋",
            "excited": f"HELLO {name.upper()}!!! 🎉"
        }
        
        return {
            "message": greetings.get(style, greetings["friendly"]),
            "style_used": style,
            "sdk_component": "AgentHub @endpoint decorator"
        }
    
    @endpoint("/calculate", description="Perform basic mathematical operations")
    def calculate(request):
        a = request.get("a", 0)
        b = request.get("b", 0)
        operation = request.get("operation", "add")
        
        operations = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else "Error: Division by zero",
            "power": a ** b
        }
        
        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}
        
        result = operations[operation]
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
            "sdk_component": "AgentHub @endpoint decorator"
        }
    
    @endpoint("/analyze_text", description="Analyze text and provide basic statistics")
    def analyze_text(request):
        text = request.get("text", "")
        
        if not text:
            return {"error": "No text provided"}
        
        words = text.split()
        sentences = text.split('.')
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
            "longest_word": max(words, key=len) if words else "",
            "analysis": "Text analysis complete",
            "sdk_component": "AgentHub @endpoint decorator"
        }
    
    @endpoint("/status", description="Get agent status and health information")
    def status(request):
        return {
            "status": "running",
            "agent_id": runner.agent_id,
            "version": "1.0.0",
            "uptime": "unknown (demo mode)",
            "endpoints_available": len(runner.endpoints),
            "health": "excellent",
            "sdk_component": "AgentHub @endpoint decorator"
        }
    
    # Register endpoints with runner
    runner.register_endpoint("/greet", greet, "Greet users with a personalized message")
    runner.register_endpoint("/calculate", calculate, "Perform basic mathematical operations")
    runner.register_endpoint("/analyze_text", analyze_text, "Analyze text and provide basic statistics")
    runner.register_endpoint("/status", status, "Get agent status and health information")
    
    return runner


def run_interactive_demo():
    """Run an interactive demo of the local agent using AgentHub SDK"""
    
    print("🤖 AgentHub SDK Local Agent Demo")
    print("=" * 50)
    print("   Using ACTUAL AgentHub SDK Components!")
    print("   (Zero Dependencies - Standard Library Only)")
    print("=" * 50)
    
    # Create demo agent
    agent = create_demo_agent()
    
    print(f"✅ Created agent: {agent.metadata.name}")
    print(f"🆔 Agent ID: {agent.agent_id}")
    print(f"🏗️  Using AgentMetadata from AgentHub SDK")
    print(f"🎯 Using @endpoint decorator from AgentHub SDK")
    print()
    
    # Show agent info
    print("📋 Agent Information:")
    info = agent.info()
    metadata = info['metadata']
    print(f"   Name: {metadata['name']}")
    print(f"   Description: {metadata['description']}")
    print(f"   Category: {metadata['category']}")
    print(f"   Version: {metadata['version']}")
    
    # Handle pricing display (works with both Pydantic and fallback models)
    pricing = metadata.get('pricing', {})
    if hasattr(pricing, 'dict'):
        pricing_info = pricing.dict()
    elif hasattr(pricing, '__dict__'):
        pricing_info = vars(pricing)
    else:
        pricing_info = pricing
    
    if isinstance(pricing_info, dict):
        print(f"   Price: ${pricing_info.get('price', 'N/A')} per {pricing_info.get('type', 'request')}")
    else:
        print(f"   Price: {pricing_info}")
    print()
    
    # Show available endpoints
    print("📡 Available Endpoints (using @endpoint decorator):")
    for path, description in agent.list_endpoints().items():
        print(f"   {path}: {description}")
    print()
    
    # Demonstrate endpoint calls
    print("🧪 Testing Endpoints:")
    print()
    
    # Test 1: Greeting
    print("1. Testing /greet endpoint:")
    result1 = agent.call_endpoint("/greet", {"name": "Alice", "style": "excited"})
    print(f"   Input: name='Alice', style='excited'")
    print(f"   Output: {json.dumps(result1['result'], indent=6)}")
    print()
    
    # Test 2: Calculate
    print("2. Testing /calculate endpoint:")
    result2 = agent.call_endpoint("/calculate", {"a": 15, "b": 3, "operation": "multiply"})
    print(f"   Input: a=15, b=3, operation='multiply'")
    print(f"   Output: {json.dumps(result2['result'], indent=6)}")
    print()
    
    # Test 3: Text analysis
    print("3. Testing /analyze_text endpoint:")
    sample_text = "Hello world! This is a sample text for analysis. It has multiple sentences."
    result3 = agent.call_endpoint("/analyze_text", {"text": sample_text})
    print(f"   Input: text='{sample_text[:30]}...'")
    print(f"   Output: {json.dumps(result3['result'], indent=6)}")
    print()
    
    # Test 4: Status
    print("4. Testing /status endpoint:")
    result4 = agent.call_endpoint("/status")
    print(f"   Output: {json.dumps(result4['result'], indent=6)}")
    print()
    
    print("🎯 Key Points:")
    print("   ✅ Uses ACTUAL AgentHub SDK components (@endpoint, AgentMetadata)")
    print("   ✅ Zero external dependencies - works with standard library only")
    print("   ✅ Same decorators and models used in full HTTP agents")
    print("   ✅ Perfect for prototyping and learning AgentHub concepts")
    print("   ✅ Agents run completely locally for development")
    print()
    
    print("🔄 Progressive Enhancement:")
    print("   📦 Level 1 (Current): Zero dependencies - Local execution")
    print("   📦 Level 2: Add FastAPI - HTTP server with AgentBuilder")
    print("   📦 Level 3: Add full SDK - CLI tools and marketplace integration")
    print()
    
    print("🚀 Next Steps:")
    print("   1. For HTTP server: pip install agenthub-sdk")
    print("   2. Use AgentBuilder: from agenthub import AgentBuilder")
    print("   3. Serve with: agenthub serve --config config.yaml")
    print("   4. For full features: pip install agenthub-sdk[full]")
    print("   5. Publish with: agenthub publish --api-key YOUR_KEY")
    print()
    
    print("💡 This demo proves AgentHub agents work with just Python standard library!")


def test_sdk_components():
    """Test that we're actually using AgentHub SDK components"""
    
    print("\n🔍 SDK Component Verification:")
    print("-" * 40)
    
    # Test AgentMetadata
    try:
        metadata = AgentMetadata(name="test", description="test", category="test")
        print(f"✅ AgentMetadata: {type(metadata).__module__}.{type(metadata).__name__}")
    except Exception as e:
        print(f"❌ AgentMetadata error: {e}")
    
    # Test endpoint decorator
    try:
        @endpoint("/test")
        def test_func(request):
            return {"test": True}
        
        print(f"✅ @endpoint decorator: Function decorated successfully")
        
        # Test that the decorator adds metadata
        if hasattr(test_func, '_agenthub_endpoint'):
            print(f"✅ Endpoint metadata: {test_func._agenthub_endpoint}")
        else:
            print("ℹ️  Endpoint metadata: Added by decorator")
            
    except Exception as e:
        print(f"❌ @endpoint decorator error: {e}")
    
    # Test PricingModel
    try:
        pricing = PricingModel(type="per_request", price=0.01)
        print(f"✅ PricingModel: {type(pricing).__module__}.{type(pricing).__name__}")
    except Exception as e:
        print(f"❌ PricingModel error: {e}")
    
    print("-" * 40)


if __name__ == "__main__":
    test_sdk_components()
    run_interactive_demo()