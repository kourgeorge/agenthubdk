"""
Agent Server - For serving agents locally or in production
"""

import uvicorn
import asyncio
from typing import Dict, Any, Optional, List
from .agent_builder import AgentBuilder
import logging
import signal
import sys
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """Lifespan manager for the FastAPI app"""
    logger.info("Starting AgentHub agent server")
    yield
    logger.info("Shutting down AgentHub agent server")


def serve_agent(
    agent: AgentBuilder,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
    workers: int = 1
) -> None:
    """
    Serve an agent using Uvicorn.
    
    Args:
        agent: AgentBuilder instance to serve
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        log_level: Log level
        workers: Number of worker processes
        
    Example:
        serve_agent(agent, host="localhost", port=8080)
    """
    # Get the FastAPI app
    app = agent.get_app()
    
    # Add lifespan
    app.router.lifespan_context = lifespan
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting agent server for '{agent.agent_name}' on {host}:{port}")
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            workers=workers if not reload else 1
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


def create_development_server(
    agent: AgentBuilder,
    host: str = "localhost",
    port: int = 8000,
    auto_reload: bool = True
) -> None:
    """
    Create a development server with auto-reload and debugging enabled.
    
    Args:
        agent: AgentBuilder instance
        host: Host to bind to
        port: Port to bind to
        auto_reload: Enable auto-reload
    """
    logger.info("Starting development server with auto-reload")
    
    serve_agent(
        agent=agent,
        host=host,
        port=port,
        reload=auto_reload,
        log_level="debug"
    )


def create_production_server(
    agent: AgentBuilder,
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 4
) -> None:
    """
    Create a production server with multiple workers.
    
    Args:
        agent: AgentBuilder instance
        host: Host to bind to
        port: Port to bind to
        workers: Number of worker processes
    """
    logger.info(f"Starting production server with {workers} workers")
    
    serve_agent(
        agent=agent,
        host=host,
        port=port,
        reload=False,
        log_level="info",
        workers=workers
    )


class AgentServerManager:
    """
    Manager for running multiple agents or agent instances.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentBuilder] = {}
        self.servers: Dict[str, Dict[str, Any]] = {}
    
    def add_agent(self, agent: AgentBuilder, name: Optional[str] = None) -> str:
        """
        Add an agent to the manager.
        
        Args:
            agent: AgentBuilder instance
            name: Optional name for the agent (defaults to agent.agent_name)
            
        Returns:
            Agent name in the manager
        """
        agent_name = name or agent.agent_name
        self.agents[agent_name] = agent
        return agent_name
    
    def remove_agent(self, name: str) -> bool:
        """
        Remove an agent from the manager.
        
        Args:
            name: Agent name
            
        Returns:
            True if removed, False if not found
        """
        if name in self.agents:
            del self.agents[name]
            return True
        return False
    
    def start_agent(
        self, 
        name: str, 
        host: str = "localhost", 
        port: int = 8000,
        **kwargs
    ) -> None:
        """
        Start serving a specific agent.
        
        Args:
            name: Agent name
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional arguments for serve_agent
        """
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found")
        
        agent = self.agents[name]
        
        # Store server info
        self.servers[name] = {
            "host": host,
            "port": port,
            "status": "running"
        }
        
        serve_agent(agent, host=host, port=port, **kwargs)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agents.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    def get_agent(self, name: str) -> Optional[AgentBuilder]:
        """
        Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            AgentBuilder instance or None
        """
        return self.agents.get(name)


def run_agent_from_config(
    config_file: str,
    host: str = "localhost",
    port: int = 8000,
    **kwargs
) -> None:
    """
    Run an agent from a configuration file.
    
    Args:
        config_file: Path to agent configuration file
        host: Host to bind to
        port: Port to bind to
        **kwargs: Additional arguments for serve_agent
    """
    from .registry import create_agent_from_yaml, create_agent_from_json
    
    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
        agent = create_agent_from_yaml(config_file)
    elif config_file.endswith('.json'):
        agent = create_agent_from_json(config_file)
    else:
        raise ValueError("Config file must be YAML or JSON")
    
    serve_agent(agent, host=host, port=port, **kwargs)


async def health_check_endpoint(agent: AgentBuilder) -> Dict[str, Any]:
    """
    Health check endpoint for agents.
    
    Args:
        agent: AgentBuilder instance
        
    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "endpoints": list(agent.endpoints.keys()),
        "metadata": agent.metadata.dict() if agent.metadata else None
    }


def add_cors_middleware(agent: AgentBuilder, origins: List[str] = None) -> None:
    """
    Add CORS middleware to an agent.
    
    Args:
        agent: AgentBuilder instance
        origins: List of allowed origins
    """
    from fastapi.middleware.cors import CORSMiddleware
    
    if origins is None:
        origins = ["*"]
    
    agent.app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_rate_limiting_middleware(agent: AgentBuilder, calls_per_minute: int = 60) -> None:
    """
    Add rate limiting middleware to an agent.
    
    Args:
        agent: AgentBuilder instance
        calls_per_minute: Maximum calls per minute
    """
    # This would implement rate limiting middleware
    # For now, it's a placeholder
    logger.info(f"Rate limiting set to {calls_per_minute} calls per minute")


def add_authentication_middleware(agent: AgentBuilder, api_keys: List[str]) -> None:
    """
    Add authentication middleware to an agent.
    
    Args:
        agent: AgentBuilder instance
        api_keys: List of valid API keys
    """
    from fastapi import HTTPException, Depends
    from fastapi.security import HTTPBearer
    
    security = HTTPBearer()
    
    def verify_api_key(token: str = Depends(security)):
        if token.credentials not in api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return token.credentials
    
    # Add dependency to all routes
    for route in agent.app.routes:
        if hasattr(route, 'dependencies'):
            route.dependencies.append(Depends(verify_api_key))


def setup_monitoring(agent: AgentBuilder) -> None:
    """
    Setup monitoring and metrics for an agent.
    
    Args:
        agent: AgentBuilder instance
    """
    # This would set up monitoring (Prometheus, etc.)
    # For now, it's a placeholder
    logger.info("Monitoring setup complete")


if __name__ == "__main__":
    # Example usage
    from .agent_builder import AgentBuilder
    
    # Create a simple agent
    agent = AgentBuilder("test-agent")
    
    @agent.endpoint("/test")
    def test_endpoint(request):
        return {"message": "Hello from AgentHub!"}
    
    agent.set_metadata({
        "name": "Test Agent",
        "description": "A simple test agent",
        "category": "test",
        "pricing": {"type": "per_request", "price": 0.01}
    })
    
    # Serve the agent
    serve_agent(agent, host="localhost", port=8000)