"""
ACP Manager - Handles dynamic ACP server creation and management for agents
"""

import asyncio
import json
import logging
import socket
import threading
import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile
import subprocess
import sys

try:
    from acp_sdk.models import Message, MessagePart
    from acp_sdk.client import Client
    ACP_AVAILABLE = True
except ImportError:
    ACP_AVAILABLE = False

logger = logging.getLogger(__name__)


class ACPServerManager:
    """
    Manages dynamic ACP servers for agent execution
    """
    
    def __init__(self):
        self.active_servers: Dict[str, Dict[str, Any]] = {}
        self.port_range_start = 9000
        self.port_range_end = 9999
        self.used_ports = set()
    
    def find_available_port(self) -> int:
        """Find an available port for the ACP server"""
        for port in range(self.port_range_start, self.port_range_end + 1):
            if port not in self.used_ports:
                try:
                    # Test if port is available
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        self.used_ports.add(port)
                        return port
                except OSError:
                    continue
        raise Exception("No available ports in range")
    
    def release_port(self, port: int):
        """Release a port back to the pool"""
        self.used_ports.discard(port)
    
    async def create_agent_server(
        self, 
        agent_id: str, 
        agent_config: Dict[str, Any],
        task_id: str
    ) -> Dict[str, Any]:
        """
        Create a dynamic ACP server for an agent
        
        Args:
            agent_id: Agent identifier
            agent_config: Agent configuration and code
            task_id: Task identifier for tracking
            
        Returns:
            Server info dict with port and connection details
        """
        if not ACP_AVAILABLE:
            raise ImportError("acp_sdk not available. Install with: pip install acp-sdk")
        
        try:
            # Find available port
            port = self.find_available_port()
            
            # Create agent server script based on configuration
            server_script = self._generate_agent_server_script(agent_config, port)
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.py', 
                delete=False
            ) as f:
                f.write(server_script)
                script_path = f.name
            
            # Start the server process
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for server to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise Exception(f"Agent server failed to start: {stderr}")
            
            server_info = {
                "agent_id": agent_id,
                "task_id": task_id,
                "port": port,
                "process": process,
                "script_path": script_path,
                "url": f"http://localhost:{port}",
                "started_at": time.time()
            }
            
            self.active_servers[task_id] = server_info
            
            logger.info(f"Created ACP server for agent {agent_id} on port {port}")
            return server_info
            
        except Exception as e:
            logger.error(f"Failed to create agent server: {e}")
            if 'port' in locals():
                self.release_port(port)
            raise
    
    def _generate_agent_server_script(self, agent_config: Dict[str, Any], port: int) -> str:
        """Generate ACP server script based on agent configuration"""
        agent_type = agent_config.get("type", "code_agent")
        agent_name = agent_config.get("name", "dynamic_agent")
        agent_description = agent_config.get("description", "Dynamic agent")
        
        # Base imports and setup
        script = f'''
import asyncio
import sys
import logging
from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server()

'''
        
        # Add agent-specific implementation based on type
        if agent_type == "code_agent":
            script += self._generate_code_agent_implementation(agent_config)
        elif agent_type == "llm_agent":
            script += self._generate_llm_agent_implementation(agent_config)
        elif agent_type == "tool_agent":
            script += self._generate_tool_agent_implementation(agent_config)
        else:
            script += self._generate_generic_agent_implementation(agent_config)
        
        # Add server startup
        script += f'''

if __name__ == "__main__":
    try:
        logger.info("Starting ACP server on port {port}")
        server.run(port={port})
    except Exception as e:
        logger.error(f"Server failed: {{e}}")
        sys.exit(1)
'''
        
        return script
    
    def _generate_code_agent_implementation(self, config: Dict[str, Any]) -> str:
        """Generate CodeAgent implementation"""
        model_id = config.get("model_id", "openai/gpt-4")
        tools = config.get("tools", ["DuckDuckGoSearchTool", "VisitWebpageTool"])
        description = config.get("description", "A code agent")
        
        tools_import = []
        tools_init = []
        
        for tool in tools:
            if tool == "DuckDuckGoSearchTool":
                tools_import.append("DuckDuckGoSearchTool")
                tools_init.append("DuckDuckGoSearchTool()")
            elif tool == "VisitWebpageTool":
                tools_import.append("VisitWebpageTool")
                tools_init.append("VisitWebpageTool()")
        
        tools_import_str = ", ".join(tools_import) if tools_import else ""
        tools_init_str = ", ".join(tools_init) if tools_init else ""
        
        return f'''
from smolagents import CodeAgent, LiteLLMModel{', ' + tools_import_str if tools_import_str else ''}
from dotenv import load_dotenv

load_dotenv()

model = LiteLLMModel(
    model_id="{model_id}",
    max_tokens=2048
)

@server.agent()
async def dynamic_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """{description}"""
    try:
        tools = [{tools_init_str}] if "{tools_init_str}" else []
        agent = CodeAgent(tools=tools, model=model)
        
        # Get the prompt from the first message
        prompt = input[0].parts[0].content
        logger.info(f"Processing prompt: {{prompt[:100]}}...")
        
        # Run the agent
        response = agent.run(prompt)
        
        # Return the response
        yield Message(parts=[MessagePart(content=str(response))])
        
    except Exception as e:
        logger.error(f"Agent execution failed: {{e}}")
        yield Message(parts=[MessagePart(content=f"Error: {{str(e)}}")])
'''
    
    def _generate_llm_agent_implementation(self, config: Dict[str, Any]) -> str:
        """Generate LLM agent implementation"""
        model_id = config.get("model_id", "openai/gpt-4")
        system_prompt = config.get("system_prompt", "You are a helpful AI assistant.")
        description = config.get("description", "An LLM agent")
        
        return f'''
from smolagents import LiteLLMModel
from dotenv import load_dotenv

load_dotenv()

model = LiteLLMModel(
    model_id="{model_id}",
    max_tokens=2048
)

@server.agent()
async def dynamic_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """{description}"""
    try:
        # Get the prompt from the first message
        user_prompt = input[0].parts[0].content
        
        # Create full prompt with system message
        full_prompt = f"{system_prompt}\\n\\nUser: {{user_prompt}}"
        
        logger.info(f"Processing LLM prompt: {{user_prompt[:100]}}...")
        
        # Generate response using the model
        response = model.complete(full_prompt)
        
        # Return the response
        yield Message(parts=[MessagePart(content=str(response))])
        
    except Exception as e:
        logger.error(f"LLM agent execution failed: {{e}}")
        yield Message(parts=[MessagePart(content=f"Error: {{str(e)}}")])
'''
    
    def _generate_tool_agent_implementation(self, config: Dict[str, Any]) -> str:
        """Generate tool-based agent implementation"""
        tools = config.get("tools", [])
        description = config.get("description", "A tool agent")
        
        return f'''
@server.agent()
async def dynamic_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """{description}"""
    try:
        # Get the prompt from the first message
        prompt = input[0].parts[0].content
        
        logger.info(f"Processing tool request: {{prompt[:100]}}...")
        
        # Simple tool execution logic
        # This would be expanded based on specific tools
        response = f"Processed tool request: {{prompt}}"
        
        # Return the response
        yield Message(parts=[MessagePart(content=response)])
        
    except Exception as e:
        logger.error(f"Tool agent execution failed: {{e}}")
        yield Message(parts=[MessagePart(content=f"Error: {{str(e)}}")])
'''
    
    def _generate_generic_agent_implementation(self, config: Dict[str, Any]) -> str:
        """Generate generic agent implementation"""
        description = config.get("description", "A generic agent")
        
        return f'''
@server.agent()
async def dynamic_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """{description}"""
    try:
        # Get the prompt from the first message
        prompt = input[0].parts[0].content
        
        logger.info(f"Processing generic request: {{prompt[:100]}}...")
        
        # Simple echo response - customize based on needs
        response = f"Agent processed: {{prompt}}"
        
        # Return the response
        yield Message(parts=[MessagePart(content=response)])
        
    except Exception as e:
        logger.error(f"Generic agent execution failed: {{e}}")
        yield Message(parts=[MessagePart(content=f"Error: {{str(e)}}")])
'''
    
    async def execute_agent_task(
        self, 
        server_info: Dict[str, Any], 
        prompt: str,
        timeout: int = 30
    ) -> str:
        """
        Execute a task on the ACP agent server
        
        Args:
            server_info: Server information from create_agent_server
            prompt: Input prompt for the agent
            timeout: Timeout in seconds
            
        Returns:
            Agent response as string
        """
        if not ACP_AVAILABLE:
            raise ImportError("acp_sdk not available")
        
        try:
            # Create ACP client
            client = Client(server_info["url"])
            
            # Create message
            message = Message(parts=[MessagePart(content=prompt)])
            
            # Send message and get response
            response = await asyncio.wait_for(
                client.send_message([message]),
                timeout=timeout
            )
            
            # Extract response content
            if response and len(response) > 0:
                return response[0].parts[0].content
            else:
                return "No response from agent"
                
        except asyncio.TimeoutError:
            raise Exception(f"Agent execution timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Failed to execute agent task: {e}")
            raise
    
    async def cleanup_server(self, task_id: str):
        """Clean up an ACP server"""
        if task_id not in self.active_servers:
            return
        
        server_info = self.active_servers[task_id]
        
        try:
            # Terminate the process
            process = server_info["process"]
            if process.poll() is None:
                process.terminate()
                
                # Wait for process to end
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    process.kill()
            
            # Clean up temporary file
            script_path = server_info["script_path"]
            try:
                Path(script_path).unlink()
            except OSError:
                pass
            
            # Release port
            self.release_port(server_info["port"])
            
            # Remove from active servers
            del self.active_servers[task_id]
            
            logger.info(f"Cleaned up ACP server for task {task_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up server for task {task_id}: {e}")
    
    async def cleanup_all_servers(self):
        """Clean up all active servers"""
        task_ids = list(self.active_servers.keys())
        for task_id in task_ids:
            await self.cleanup_server(task_id)
    
    def get_server_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an ACP server"""
        if task_id not in self.active_servers:
            return None
        
        server_info = self.active_servers[task_id]
        process = server_info["process"]
        
        return {
            "task_id": task_id,
            "agent_id": server_info["agent_id"],
            "port": server_info["port"],
            "url": server_info["url"],
            "started_at": server_info["started_at"],
            "running": process.poll() is None,
            "uptime": time.time() - server_info["started_at"]
        }


# Global ACP manager instance
_acp_manager: Optional[ACPServerManager] = None


def get_acp_manager() -> ACPServerManager:
    """Get the global ACP manager instance"""
    global _acp_manager
    if _acp_manager is None:
        _acp_manager = ACPServerManager()
    return _acp_manager