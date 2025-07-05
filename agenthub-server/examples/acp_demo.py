"""
ACP-based AgentHub Server Demo

This demo showcases the new dynamic agent hiring system using the Agent Communication Protocol (ACP).
Instead of pre-running servers, agents are dynamically spawned when tasks are requested.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

import httpx
from agenthub_server.server import create_hub_server
from agenthub_server.models import AgentMetadata, TaskRequest, PricingModel, PricingType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ACPAgentHubDemo:
    """Demo of the ACP-based AgentHub system"""
    
    def __init__(self, hub_port: int = 8080):
        self.hub_port = hub_port
        self.hub_url = f"http://localhost:{hub_port}"
        self.hub_server = None
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def setup_hub(self):
        """Setup the AgentHub server"""
        logger.info("Setting up AgentHub server...")
        
        # Create hub server
        self.hub_server = create_hub_server(
            database_url="sqlite:///acp_demo.db",
            enable_cors=True,
            require_auth=False  # Disable auth for demo
        )
        
        # In a real scenario, you would start the server in a separate process
        # For this demo, we'll assume it's running
        logger.info(f"Hub server ready at {self.hub_url}")
        
    async def register_agents(self):
        """Register various types of ACP agents"""
        logger.info("Registering ACP agents...")
        
        # 1. Health Assistant Agent (CodeAgent with tools)
        health_agent = AgentMetadata(
            name="Health Assistant",
            description="Medical information agent that helps with health-related questions",
            version="1.0.0",
            category="healthcare",
            tags=["health", "medical", "assistant"],
            author="HealthTech Labs",
            pricing=PricingModel(
                type=PricingType.PER_REQUEST,
                price=0.50,
                currency="USD"
            )
        )
        
        health_config = {
            "type": "code_agent",
            "name": "health_assistant",
            "description": "Medical information assistant",
            "model_id": "openai/gpt-4",
            "tools": ["DuckDuckGoSearchTool", "VisitWebpageTool"],
            "system_prompt": "You are a medical information assistant. Provide helpful, accurate health information but always remind users to consult healthcare professionals for medical advice."
        }
        
        # Register health agent
        response = await self.client.post(
            f"{self.hub_url}/agents/register",
            json={
                "metadata": health_agent.dict(),
                "agent_config": health_config,
                "deployment_type": "acp"
            }
        )
        
        if response.status_code == 200:
            health_agent_id = response.json()["agent_id"]
            logger.info(f"✓ Registered Health Assistant: {health_agent_id}")
        else:
            logger.error(f"Failed to register health agent: {response.text}")
            return
        
        # 2. Data Analyst Agent (LLM-based)
        analyst_agent = AgentMetadata(
            name="Data Analyst Assistant",
            description="Data analysis and insights agent",
            version="1.2.0",
            category="analytics",
            tags=["data", "analysis", "statistics"],
            author="DataInsights Inc",
            pricing=PricingModel(
                type=PricingType.PER_REQUEST,
                price=0.75,
                currency="USD"
            )
        )
        
        analyst_config = {
            "type": "llm_agent",
            "name": "data_analyst",
            "description": "Data analysis assistant",
            "model_id": "openai/gpt-4",
            "system_prompt": "You are a data analyst assistant. Help users analyze data, create insights, and provide statistical interpretations. Always explain your reasoning and suggest additional analysis when appropriate."
        }
        
        # Register analyst agent
        response = await self.client.post(
            f"{self.hub_url}/agents/register",
            json={
                "metadata": analyst_agent.dict(),
                "agent_config": analyst_config,
                "deployment_type": "acp"
            }
        )
        
        if response.status_code == 200:
            analyst_agent_id = response.json()["agent_id"]
            logger.info(f"✓ Registered Data Analyst: {analyst_agent_id}")
        else:
            logger.error(f"Failed to register analyst agent: {response.text}")
            return
        
        # 3. Creative Writing Agent (Generic)
        writer_agent = AgentMetadata(
            name="Creative Writer",
            description="Creative writing and storytelling agent",
            version="1.0.0",
            category="creative",
            tags=["writing", "creative", "stories"],
            author="CreativeAI Studio",
            pricing=PricingModel(
                type=PricingType.PER_REQUEST,
                price=0.25,
                currency="USD"
            )
        )
        
        writer_config = {
            "type": "llm_agent",
            "name": "creative_writer",
            "description": "Creative writing assistant",
            "model_id": "openai/gpt-4",
            "system_prompt": "You are a creative writing assistant. Help users with storytelling, character development, plot creation, and creative writing techniques. Be imaginative and inspiring while providing practical advice."
        }
        
        # Register writer agent
        response = await self.client.post(
            f"{self.hub_url}/agents/register",
            json={
                "metadata": writer_agent.dict(),
                "agent_config": writer_config,
                "deployment_type": "acp"
            }
        )
        
        if response.status_code == 200:
            writer_agent_id = response.json()["agent_id"]
            logger.info(f"✓ Registered Creative Writer: {writer_agent_id}")
        else:
            logger.error(f"Failed to register writer agent: {response.text}")
            return
        
        return {
            "health_agent_id": health_agent_id,
            "analyst_agent_id": analyst_agent_id,
            "writer_agent_id": writer_agent_id
        }
    
    async def discover_agents(self):
        """Discover available agents"""
        logger.info("Discovering available agents...")
        
        response = await self.client.get(f"{self.hub_url}/agents")
        
        if response.status_code == 200:
            agents = response.json()["agents"]
            logger.info(f"Found {len(agents)} agents:")
            for agent in agents:
                logger.info(f"  - {agent['name']} ({agent['category']}) - {agent['description']}")
            return agents
        else:
            logger.error(f"Failed to discover agents: {response.text}")
            return []
    
    async def hire_agent(self, agent_id: str, task_description: str) -> Dict[str, Any]:
        """Hire an agent to perform a task"""
        logger.info(f"Hiring agent {agent_id} for task: {task_description}")
        
        # Create task request
        task_request = TaskRequest(
            agent_id=agent_id,
            endpoint="",  # Not needed for ACP agents
            parameters={
                "prompt": task_description
            },
            timeout=30
        )
        
        # Submit task
        response = await self.client.post(
            f"{self.hub_url}/tasks",
            json=task_request.dict()
        )
        
        if response.status_code == 200:
            task_info = response.json()
            task_id = task_info["task_id"]
            logger.info(f"✓ Task submitted: {task_id}")
            
            # Wait for task completion
            return await self.wait_for_task(task_id)
        else:
            logger.error(f"Failed to submit task: {response.text}")
            return None
    
    async def wait_for_task(self, task_id: str, max_wait: int = 60) -> Dict[str, Any]:
        """Wait for task completion"""
        logger.info(f"Waiting for task {task_id} to complete...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = await self.client.get(f"{self.hub_url}/tasks/{task_id}")
            
            if response.status_code == 200:
                task_info = response.json()
                status = task_info["status"]
                
                if status == "completed":
                    logger.info(f"✓ Task {task_id} completed successfully")
                    return task_info
                elif status == "failed":
                    logger.error(f"✗ Task {task_id} failed: {task_info.get('error', 'Unknown error')}")
                    return task_info
                else:
                    logger.info(f"Task {task_id} status: {status}")
                    await asyncio.sleep(2)
            else:
                logger.error(f"Failed to get task status: {response.text}")
                break
        
        logger.error(f"Task {task_id} did not complete within {max_wait} seconds")
        return None
    
    async def demo_scenarios(self, agent_ids: Dict[str, str]):
        """Run demonstration scenarios"""
        logger.info("Running demonstration scenarios...")
        
        # Scenario 1: Health Question
        logger.info("\n=== Scenario 1: Health Question ===")
        health_result = await self.hire_agent(
            agent_ids["health_agent_id"],
            "What are the symptoms of vitamin D deficiency and how can I improve my vitamin D levels naturally?"
        )
        
        if health_result and health_result["status"] == "completed":
            logger.info("Health Assistant Response:")
            logger.info(health_result["result"]["response"])
        
        # Scenario 2: Data Analysis
        logger.info("\n=== Scenario 2: Data Analysis ===")
        analyst_result = await self.hire_agent(
            agent_ids["analyst_agent_id"],
            "I have sales data showing Q1: $10k, Q2: $15k, Q3: $18k, Q4: $22k. What insights can you provide about this trend?"
        )
        
        if analyst_result and analyst_result["status"] == "completed":
            logger.info("Data Analyst Response:")
            logger.info(analyst_result["result"]["response"])
        
        # Scenario 3: Creative Writing
        logger.info("\n=== Scenario 3: Creative Writing ===")
        writer_result = await self.hire_agent(
            agent_ids["writer_agent_id"],
            "Help me create a character for a sci-fi story: a space engineer who discovers something unusual on a distant planet."
        )
        
        if writer_result and writer_result["status"] == "completed":
            logger.info("Creative Writer Response:")
            logger.info(writer_result["result"]["response"])
        
        # Scenario 4: Parallel Tasks
        logger.info("\n=== Scenario 4: Parallel Tasks ===")
        logger.info("Submitting multiple tasks in parallel...")
        
        tasks = [
            self.hire_agent(agent_ids["health_agent_id"], "What foods are rich in antioxidants?"),
            self.hire_agent(agent_ids["analyst_agent_id"], "What's the difference between correlation and causation?"),
            self.hire_agent(agent_ids["writer_agent_id"], "Give me a creative prompt for a mystery story.")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i+1} failed: {result}")
            elif result and result["status"] == "completed":
                logger.info(f"Task {i+1} completed: {result['result']['response'][:100]}...")
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up...")
        await self.client.aclose()
        
        # Clean up demo database
        db_path = Path("acp_demo.db")
        if db_path.exists():
            db_path.unlink()
            logger.info("Cleaned up demo database")
    
    async def run_demo(self):
        """Run the complete demo"""
        try:
            # Setup
            await self.setup_hub()
            
            # Register agents
            agent_ids = await self.register_agents()
            if not agent_ids:
                logger.error("Failed to register agents, stopping demo")
                return
            
            # Discover agents
            agents = await self.discover_agents()
            
            # Wait a moment for everything to initialize
            await asyncio.sleep(2)
            
            # Run demonstration scenarios
            await self.demo_scenarios(agent_ids)
            
            logger.info("\n=== Demo completed successfully! ===")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            
        finally:
            await self.cleanup()


async def main():
    """Main demo function"""
    logger.info("Starting ACP-based AgentHub Demo")
    logger.info("=" * 50)
    
    # Note: In a real scenario, you would start the hub server first
    logger.info("Please start the AgentHub server first:")
    logger.info("  python -m agenthub_server.cli serve --port 8080 --no-auth")
    logger.info("Then run this demo in another terminal")
    
    # Wait for user to start the server
    input("Press Enter when the server is running...")
    
    demo = ACPAgentHubDemo(hub_port=8080)
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())