#!/usr/bin/env python3
"""
Simple Local Agent Demo

This demo shows how AgentHub agents work locally without needing
the full AgentHub backend infrastructure.
"""

import json
import uuid
from typing import Dict, Any, Callable

# Simplified version of AgentBuilder for demonstration
class SimpleAgent:
    """Simplified agent that demonstrates local functionality"""
    
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())[:8]
        self.endpoints = {}
        self.metadata = {}
        
    def endpoint(self, path: str, description: str = ""):
        """Decorator to register endpoints"""
        def decorator(func: Callable):
            self.endpoints[path] = {
                "function": func,
                "description": description
            }
            return func
        return decorator
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set agent metadata"""
        self.metadata = metadata
    
    def call_endpoint(self, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simulate calling an endpoint locally"""
        if path not in self.endpoints:
            return {"error": f"Endpoint {path} not found"}
        
        # Create a simple request object
        request = type('Request', (), {
            'json': data or {},
            'query_params': {},
            'headers': {}
        })()
        
        try:
            result = self.endpoints[path]["function"](request)
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
            "name": self.name,
            "metadata": self.metadata,
            "endpoints": self.list_endpoints()
        }

def create_demo_agent():
    """Create a demonstration agent"""
    
    # Create agent
    agent = SimpleAgent("demo-agent")
    
    # Add endpoints
    @agent.endpoint("/greet", "Greet users with a personalized message")
    def greet(request):
        name = request.json.get("name", "World")
        style = request.json.get("style", "friendly")
        
        greetings = {
            "friendly": f"Hello there, {name}! 😊",
            "formal": f"Good day, {name}.",
            "casual": f"Hey {name}! 👋",
            "excited": f"HELLO {name.upper()}!!! 🎉"
        }
        
        return {
            "message": greetings.get(style, greetings["friendly"]),
            "style_used": style
        }
    
    @agent.endpoint("/calculate", "Perform basic mathematical operations")
    def calculate(request):
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
        operation = request.json.get("operation", "add")
        
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
            "result": result
        }
    
    @agent.endpoint("/analyze_text", "Analyze text and provide basic statistics")
    def analyze_text(request):
        text = request.json.get("text", "")
        
        if not text:
            return {"error": "No text provided"}
        
        words = text.split()
        sentences = text.split('.')
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "longest_word": max(words, key=len) if words else "",
            "analysis": "Text analysis complete"
        }
    
    @agent.endpoint("/status", "Get agent status and health information")
    def status(request):
        return {
            "status": "running",
            "agent_id": agent.agent_id,
            "version": "1.0.0",
            "uptime": "unknown (demo mode)",
            "endpoints_available": len(agent.endpoints),
            "health": "excellent"
        }
    
    # Set metadata
    agent.set_metadata({
        "name": "Demo Local Agent",
        "description": "A demonstration agent running locally",
        "category": "demo",
        "version": "1.0.0",
        "pricing": {"type": "per_request", "price": 0.001},
        "author": "AgentHub SDK Demo"
    })
    
    return agent

def run_interactive_demo():
    """Run an interactive demo of the local agent"""
    
    print("🤖 AgentHub Local Agent Demo")
    print("=" * 40)
    
    # Create demo agent
    agent = create_demo_agent()
    
    print(f"✅ Created agent: {agent.name}")
    print(f"🆔 Agent ID: {agent.agent_id}")
    print()
    
    # Show agent info
    print("📋 Agent Information:")
    info = agent.info()
    print(f"   Name: {info['metadata']['name']}")
    print(f"   Description: {info['metadata']['description']}")
    print(f"   Category: {info['metadata']['category']}")
    print(f"   Price: ${info['metadata']['pricing']['price']}")
    print()
    
    # Show available endpoints
    print("📡 Available Endpoints:")
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
    print("   ✅ Agents run completely locally")
    print("   ✅ No external server required for basic functionality")
    print("   ✅ Easy to test and develop agents locally")
    print("   ✅ Full AgentHub SDK provides HTTP server (FastAPI)")
    print("   ✅ Agents can be published to marketplace when ready")
    print()
    
    print("🚀 Next Steps:")
    print("   1. Install full SDK: pip install agenthub-sdk")
    print("   2. Use AgentBuilder for HTTP endpoints")
    print("   3. Serve with: agenthub serve --config config.yaml")
    print("   4. Publish with: agenthub publish --api-key YOUR_KEY")

if __name__ == "__main__":
    run_interactive_demo()