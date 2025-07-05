"""
AgentHub Server Demo - Complete example of the AgentHub marketplace server

This example demonstrates:
1. Creating multiple AI agents
2. Starting the AgentHub marketplace server
3. Registering agents with the hub
4. Using the marketplace to discover and hire agents
5. Monitoring agent performance and analytics

Usage:
    python examples/agenthub_server_demo.py
"""

import asyncio
import time
import threading
import json
from pathlib import Path
import logging

# AgentHub imports
from agenthub import AgentBuilder
from agenthub.hub_server import create_hub_server, serve_hub
from agenthub.database import init_database
from agenthub.client import AgentHubClient
from agenthub.models import AgentMetadata, TaskRequest
from agenthub.server import serve_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_calculator_agent():
    """Create a calculator agent"""
    agent = AgentBuilder("calculator-agent")
    
    @agent.endpoint("/add", description="Add two numbers")
    def add(request):
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
        result = a + b
        return {"result": result, "operation": "addition", "inputs": {"a": a, "b": b}}
    
    @agent.endpoint("/multiply", description="Multiply two numbers")
    def multiply(request):
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
        result = a * b
        return {"result": result, "operation": "multiplication", "inputs": {"a": a, "b": b}}
    
    @agent.endpoint("/divide", description="Divide two numbers")
    def divide(request):
        a = request.json.get("a", 0)
        b = request.json.get("b", 1)
        if b == 0:
            return {"error": "Division by zero", "inputs": {"a": a, "b": b}}
        result = a / b
        return {"result": result, "operation": "division", "inputs": {"a": a, "b": b}}
    
    # Set metadata
    agent.set_metadata({
        "name": "Calculator Agent",
        "description": "Performs basic arithmetic operations with high precision",
        "category": "utility",
        "version": "1.0.0",
        "author": "AgentHub Demo",
        "license": "MIT",
        "tags": ["math", "calculator", "utility"],
        "pricing": {"type": "per_request", "price": 0.01, "currency": "USD"}
    })
    
    return agent


def create_text_processor_agent():
    """Create a text processing agent"""
    agent = AgentBuilder("text-processor-agent")
    
    @agent.endpoint("/uppercase", description="Convert text to uppercase")
    def uppercase(request):
        text = request.json.get("text", "")
        return {"result": text.upper(), "original": text, "operation": "uppercase"}
    
    @agent.endpoint("/count_words", description="Count words in text")
    def count_words(request):
        text = request.json.get("text", "")
        words = len(text.split())
        characters = len(text)
        return {
            "word_count": words,
            "character_count": characters,
            "original": text,
            "operation": "word_count"
        }
    
    @agent.endpoint("/reverse", description="Reverse text")
    def reverse(request):
        text = request.json.get("text", "")
        return {"result": text[::-1], "original": text, "operation": "reverse"}
    
    # Set metadata
    agent.set_metadata({
        "name": "Text Processor Agent",
        "description": "Processes text with various transformations and analysis",
        "category": "text_processing",
        "version": "1.2.0",
        "author": "AgentHub Demo",
        "license": "MIT",
        "tags": ["text", "processing", "nlp", "utility"],
        "pricing": {"type": "per_request", "price": 0.005, "currency": "USD"}
    })
    
    return agent


def create_data_analyzer_agent():
    """Create a data analysis agent"""
    agent = AgentBuilder("data-analyzer-agent")
    
    @agent.endpoint("/analyze_numbers", description="Analyze a list of numbers")
    def analyze_numbers(request):
        numbers = request.json.get("numbers", [])
        if not numbers:
            return {"error": "No numbers provided"}
        
        try:
            total = sum(numbers)
            count = len(numbers)
            average = total / count
            minimum = min(numbers)
            maximum = max(numbers)
            
            return {
                "count": count,
                "sum": total,
                "average": average,
                "min": minimum,
                "max": maximum,
                "range": maximum - minimum,
                "operation": "number_analysis"
            }
        except Exception as e:
            return {"error": str(e)}
    
    @agent.endpoint("/find_patterns", description="Find patterns in data")
    def find_patterns(request):
        data = request.json.get("data", [])
        pattern_type = request.json.get("pattern_type", "frequency")
        
        if pattern_type == "frequency":
            frequency = {}
            for item in data:
                frequency[str(item)] = frequency.get(str(item), 0) + 1
            return {"frequency": frequency, "most_common": max(frequency.items(), key=lambda x: x[1]) if frequency else None}
        
        return {"error": "Unsupported pattern type"}
    
    # Set metadata
    agent.set_metadata({
        "name": "Data Analyzer Agent",
        "description": "Analyzes datasets and finds patterns in data",
        "category": "analytics",
        "version": "2.0.0",
        "author": "AgentHub Demo",
        "license": "Apache-2.0",
        "tags": ["data", "analytics", "statistics", "patterns"],
        "pricing": {"type": "per_request", "price": 0.02, "currency": "USD"}
    })
    
    return agent


def start_agent_servers(agents_config):
    """Start agent servers in separate threads"""
    def start_agent_server(agent, port):
        try:
            logger.info(f"Starting {agent.agent_name} on port {port}")
            serve_agent(agent, host="localhost", port=port, log_level="warning")
        except Exception as e:
            logger.error(f"Failed to start {agent.agent_name}: {e}")
    
    threads = []
    for agent, port in agents_config:
        thread = threading.Thread(target=start_agent_server, args=(agent, port), daemon=True)
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Give each server time to start
    
    return threads


def start_hub_server():
    """Start the AgentHub marketplace server"""
    def run_hub():
        try:
            # Initialize database
            db = init_database("sqlite:///agenthub_demo.db")
            
            # Create and start server
            server = create_hub_server(
                database_url="sqlite:///agenthub_demo.db",
                enable_cors=True,
                require_auth=False  # Disable auth for demo
            )
            
            logger.info("Starting AgentHub marketplace server on port 8080")
            serve_hub(
                server=server,
                host="localhost",
                port=8080,
                log_level="warning"
            )
        except Exception as e:
            logger.error(f"Failed to start hub server: {e}")
    
    thread = threading.Thread(target=run_hub, daemon=True)
    thread.start()
    time.sleep(2)  # Give server time to start
    return thread


async def register_agents_with_hub(agents_config):
    """Register agents with the AgentHub marketplace"""
    # Initialize database directly for registration
    db = init_database("sqlite:///agenthub_demo.db")
    
    agent_ids = []
    for agent, port in agents_config:
        try:
            agent_id = db.register_agent(
                agent.metadata,
                endpoint_url=f"http://localhost:{port}"
            )
            agent_ids.append((agent_id, agent.agent_name))
            logger.info(f"Registered {agent.agent_name} with ID: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to register {agent.agent_name}: {e}")
    
    return agent_ids


async def demonstrate_marketplace_usage():
    """Demonstrate using the AgentHub marketplace"""
    logger.info("🌟 Demonstrating AgentHub Marketplace Usage")
    
    # Create a client (no API key needed for demo)
    import httpx
    base_url = "http://localhost:8080"
    
    try:
        # Test server health
        logger.info("📊 Checking server health...")
        response = httpx.get(f"{base_url}/health", timeout=10.0)
        health = response.json()
        logger.info(f"✅ Server healthy - {health['agents_count']} agents registered")
        
        # Search for agents
        logger.info("🔍 Searching for agents...")
        response = httpx.get(f"{base_url}/agents", timeout=10.0)
        agents_data = response.json()
        agents = agents_data["agents"]
        
        logger.info(f"📋 Found {len(agents)} agents:")
        for agent in agents:
            logger.info(f"  🤖 {agent['name']} ({agent['category']}) - {agent['total_tasks']} tasks")
        
        # Hire the calculator agent
        calculator_agent = next((a for a in agents if "Calculator" in a['name']), None)
        if calculator_agent:
            logger.info("🧮 Hiring Calculator Agent for addition...")
            
            task_data = {
                "agent_id": calculator_agent['id'],
                "endpoint": "/add",
                "parameters": {"a": 15, "b": 27}
            }
            
            response = httpx.post(f"{base_url}/tasks", json=task_data, timeout=10.0)
            task = response.json()
            task_id = task["task_id"]
            
            # Wait for task completion
            for i in range(10):
                await asyncio.sleep(1)
                response = httpx.get(f"{base_url}/tasks/{task_id}", timeout=10.0)
                task_status = response.json()
                
                if task_status["status"] == "completed":
                    result = task_status["result"]
                    logger.info(f"✅ Task completed! Result: 15 + 27 = {result['result']['result']}")
                    logger.info(f"⏱️  Execution time: {task_status['execution_time']:.3f}s")
                    break
                elif task_status["status"] == "failed":
                    logger.error(f"❌ Task failed: {task_status.get('error')}")
                    break
        
        # Hire the text processor agent
        text_agent = next((a for a in agents if "Text" in a['name']), None)
        if text_agent:
            logger.info("📝 Hiring Text Processor Agent...")
            
            task_data = {
                "agent_id": text_agent['id'],
                "endpoint": "/count_words",
                "parameters": {"text": "Hello, this is a test message for the AgentHub marketplace demo!"}
            }
            
            response = httpx.post(f"{base_url}/tasks", json=task_data, timeout=10.0)
            task = response.json()
            task_id = task["task_id"]
            
            # Wait for task completion
            for i in range(10):
                await asyncio.sleep(1)
                response = httpx.get(f"{base_url}/tasks/{task_id}", timeout=10.0)
                task_status = response.json()
                
                if task_status["status"] == "completed":
                    result = task_status["result"]
                    logger.info(f"✅ Text analysis completed!")
                    logger.info(f"📊 Words: {result['result']['word_count']}, Characters: {result['result']['character_count']}")
                    break
        
        # Hire the data analyzer agent
        data_agent = next((a for a in agents if "Data" in a['name']), None)
        if data_agent:
            logger.info("📈 Hiring Data Analyzer Agent...")
            
            task_data = {
                "agent_id": data_agent['id'],
                "endpoint": "/analyze_numbers",
                "parameters": {"numbers": [1, 5, 10, 15, 20, 25, 30]}
            }
            
            response = httpx.post(f"{base_url}/tasks", json=task_data, timeout=10.0)
            task = response.json()
            task_id = task["task_id"]
            
            # Wait for task completion
            for i in range(10):
                await asyncio.sleep(1)
                response = httpx.get(f"{base_url}/tasks/{task_id}", timeout=10.0)
                task_status = response.json()
                
                if task_status["status"] == "completed":
                    result = task_status["result"]
                    analysis = result['result']
                    logger.info(f"✅ Data analysis completed!")
                    logger.info(f"📊 Count: {analysis['count']}, Average: {analysis['average']:.2f}, Range: {analysis['range']}")
                    break
        
        # Batch task example
        logger.info("🔄 Demonstrating batch tasks...")
        batch_tasks = [
            {
                "agent_id": calculator_agent['id'],
                "endpoint": "/multiply",
                "parameters": {"a": 6, "b": 7}
            },
            {
                "agent_id": text_agent['id'],
                "endpoint": "/uppercase",
                "parameters": {"text": "hello world"}
            }
        ]
        
        response = httpx.post(f"{base_url}/tasks/batch", json=batch_tasks, timeout=10.0)
        batch_result = response.json()
        logger.info(f"🚀 Submitted {len(batch_result['tasks'])} batch tasks")
        
        # Show agent analytics
        if calculator_agent:
            logger.info("📈 Getting agent analytics...")
            response = httpx.get(f"{base_url}/agents/{calculator_agent['id']}/analytics", timeout=10.0)
            analytics = response.json()
            logger.info(f"📊 Calculator Agent Analytics:")
            logger.info(f"   Total tasks: {analytics['total_tasks']}")
            logger.info(f"   Success rate: {analytics['success_rate']:.1%}")
            logger.info(f"   Avg execution time: {analytics['average_execution_time']:.3f}s")
        
    except Exception as e:
        logger.error(f"❌ Marketplace demo failed: {e}")


async def main():
    """Main demo function"""
    logger.info("🚀 Starting AgentHub Server Demo")
    
    # Create agents
    logger.info("🤖 Creating agents...")
    calculator = create_calculator_agent()
    text_processor = create_text_processor_agent()
    data_analyzer = create_data_analyzer_agent()
    
    agents_config = [
        (calculator, 8001),
        (text_processor, 8002),
        (data_analyzer, 8003)
    ]
    
    # Start agent servers
    logger.info("🖥️  Starting agent servers...")
    agent_threads = start_agent_servers(agents_config)
    
    # Start hub server
    logger.info("🏪 Starting AgentHub marketplace server...")
    hub_thread = start_hub_server()
    
    # Wait for servers to be ready
    await asyncio.sleep(3)
    
    # Register agents with hub
    logger.info("📝 Registering agents with marketplace...")
    agent_ids = await register_agents_with_hub(agents_config)
    
    # Demonstrate marketplace usage
    await asyncio.sleep(2)
    await demonstrate_marketplace_usage()
    
    # Keep demo running
    logger.info("🎯 Demo completed! Servers will continue running...")
    logger.info("💡 You can now:")
    logger.info("   - Visit http://localhost:8080/health to check server status")
    logger.info("   - Use the CLI: python -m agenthub.hub_cli list-agents")
    logger.info("   - Test agents directly: curl http://localhost:8001/add -d '{\"a\":5,\"b\":3}' -H 'Content-Type: application/json'")
    logger.info("   - Press Ctrl+C to stop")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Stopping demo...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Demo stopped by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()