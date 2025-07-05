#!/usr/bin/env python3
"""
Local HTTP Agent Demo

This shows how to create a local agent that serves HTTP endpoints
using only Python standard library (no external dependencies).
"""

import json
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class LocalAgent:
    """Local agent that can serve HTTP endpoints"""
    
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())[:8]
        self.endpoints = {}
        self.metadata = {}
        
    def endpoint(self, path: str, method: str = "POST", description: str = ""):
        """Decorator to register endpoints"""
        def decorator(func):
            self.endpoints[path] = {
                "function": func,
                "method": method.upper(),
                "description": description
            }
            return func
        return decorator
    
    def set_metadata(self, metadata):
        """Set agent metadata"""
        self.metadata = metadata
    
    def process_request(self, path: str, method: str, data: dict = None) -> dict:
        """Process a request to an endpoint"""
        if path not in self.endpoints:
            return {"error": f"Endpoint {path} not found", "status": 404}
        
        endpoint = self.endpoints[path]
        if endpoint["method"] != method:
            return {"error": f"Method {method} not allowed for {path}", "status": 405}
        
        # Create request object
        request = type('Request', (), {
            'json': data or {},
            'query_params': {},
            'headers': {},
            'method': method,
            'path': path
        })()
        
        try:
            result = endpoint["function"](request)
            return {
                "agent_id": self.agent_id,
                "endpoint": path,
                "result": result,
                "status": 200
            }
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "endpoint": path,
                "error": str(e),
                "status": 500
            }

class AgentHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the agent"""
    
    def __init__(self, agent, *args, **kwargs):
        self.agent = agent
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/":
            self.send_agent_info()
        elif parsed.path == "/health":
            self.send_health_check()
        else:
            response = self.agent.process_request(parsed.path, "GET")
            self.send_json_response(response)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            data = {}
        
        response = self.agent.process_request(parsed.path, "POST", data)
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """Send a JSON response"""
        status_code = data.pop("status", 200)
        response_body = json.dumps(data, indent=2).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.end_headers()
        self.wfile.write(response_body)
    
    def send_agent_info(self):
        """Send agent information"""
        info = {
            "agent_id": self.agent.agent_id,
            "name": self.agent.name,
            "metadata": self.agent.metadata,
            "endpoints": {
                path: {"method": info["method"], "description": info["description"]}
                for path, info in self.agent.endpoints.items()
            }
        }
        self.send_json_response(info)
    
    def send_health_check(self):
        """Send health check response"""
        health = {
            "status": "healthy",
            "agent_id": self.agent.agent_id,
            "endpoints": len(self.agent.endpoints)
        }
        self.send_json_response(health)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"🌐 {self.address_string()} - {format % args}")

def create_demo_http_agent():
    """Create a demo agent with HTTP endpoints"""
    
    agent = LocalAgent("http-demo-agent")
    
    @agent.endpoint("/greet", "POST", "Greet users")
    def greet(request):
        name = request.json.get("name", "World")
        return {"message": f"Hello, {name}! 🌟"}
    
    @agent.endpoint("/calculate", "POST", "Calculate math operations")
    def calculate(request):
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
        op = request.json.get("operation", "add")
        
        ops = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else "Error: Division by zero"
        }
        
        return {"result": ops.get(op, "Unknown operation")}
    
    @agent.endpoint("/status", "GET", "Get agent status")
    def status(request):
        return {
            "status": "running",
            "version": "1.0.0",
            "agent_id": agent.agent_id
        }
    
    agent.set_metadata({
        "name": "HTTP Demo Agent",
        "description": "A local HTTP agent demo",
        "category": "demo",
        "version": "1.0.0"
    })
    
    return agent

def serve_agent(agent, host="localhost", port=8000):
    """Serve the agent over HTTP"""
    
    def handler(*args, **kwargs):
        return AgentHTTPHandler(agent, *args, **kwargs)
    
    server = HTTPServer((host, port), handler)
    
    print(f"🚀 Starting agent server: {agent.name}")
    print(f"🆔 Agent ID: {agent.agent_id}")
    print(f"🌐 Server running at: http://{host}:{port}")
    print(f"📋 Agent info: http://{host}:{port}/")
    print(f"❤️ Health check: http://{host}:{port}/health")
    print()
    print("📡 Available endpoints:")
    for path, info in agent.endpoints.items():
        print(f"   {info['method']} {path} - {info['description']}")
    print()
    print("💡 Example requests:")
    print(f"   curl http://{host}:{port}/health")
    print(f"   curl -X POST http://{host}:{port}/greet -H 'Content-Type: application/json' -d '{{\"name\": \"Alice\"}}'")
    print(f"   curl -X POST http://{host}:{port}/calculate -H 'Content-Type: application/json' -d '{{\"a\": 10, \"b\": 5, \"operation\": \"multiply\"}}'")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    import sys
    
    # Create and serve the agent
    agent = create_demo_http_agent()
    
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    serve_agent(agent, port=port)