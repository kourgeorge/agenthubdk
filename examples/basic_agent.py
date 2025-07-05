"""
Basic Agent Example

This example demonstrates how to create a simple agent using the AgentHub SDK.
"""

import os
from agenthub import AgentBuilder, publish_agent

def create_basic_agent():
    """Create a basic agent with simple endpoints"""
    
    # Create agent builder
    agent = AgentBuilder("basic-agent")
    
    @agent.endpoint("/greet", description="Greet users")
    def greet(request):
        """Greet a user"""
        name = request.json.get("name", "World")
        return {"message": f"Hello, {name}!"}
    
    @agent.endpoint("/echo", description="Echo input")
    def echo(request):
        """Echo the input back"""
        message = request.json.get("message", "")
        return {"echo": message}
    
    @agent.endpoint("/calculate", description="Basic calculations")
    def calculate(request):
        """Perform basic calculations"""
        operation = request.json.get("operation", "add")
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"error": "Division by zero"}
            result = a / b
        else:
            return {"error": "Unknown operation"}
        
        return {"result": result}
    
    @agent.endpoint("/status", method="GET", description="Get agent status")
    def status(request):
        """Get agent status"""
        return {
            "status": "running",
            "version": "1.0.0",
            "uptime": "unknown"
        }
    
    # Set agent metadata
    agent.set_metadata({
        "name": "Basic Agent",
        "description": "A simple agent with basic functionality",
        "category": "utility",
        "version": "1.0.0",
        "tags": ["basic", "utility", "example"],
        "pricing": {
            "type": "per_request",
            "price": 0.001
        },
        "author": "AgentHub Team",
        "license": "MIT"
    })
    
    return agent

if __name__ == "__main__":
    # Create the agent
    agent = create_basic_agent()
    
    # Option 1: Serve locally for development
    from agenthub.server import serve_agent
    serve_agent(agent, host="localhost", port=8000, reload=True)
    
    # Option 2: Publish to AgentHub (uncomment to use)
    # publish_agent(agent, api_key=os.getenv("AGENTHUB_API_KEY"))