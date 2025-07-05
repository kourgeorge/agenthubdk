"""
AgentHub Python SDK

A comprehensive SDK for creating, registering, and managing AI agents
in the AgentHub ecosystem.
"""

__version__ = "0.1.0"
__author__ = "AgentHub Team"
__email__ = "support@agenthub.ai"

# Core imports that should always work
from .models import AgentMetadata, PricingModel, AgentEndpoint
from .decorators import endpoint, expose

# Optional imports that require external dependencies
_optional_imports = {}

try:
    from .agent_builder import AgentBuilder
    _optional_imports['AgentBuilder'] = AgentBuilder
except ImportError as e:
    def AgentBuilder(*args, **kwargs):
        raise ImportError(f"AgentBuilder requires FastAPI. Install with: pip install fastapi uvicorn\nOriginal error: {e}")
    _optional_imports['AgentBuilder'] = AgentBuilder

try:
    from .client import AgentHubClient
    _optional_imports['AgentHubClient'] = AgentHubClient
except ImportError as e:
    def AgentHubClient(*args, **kwargs):
        raise ImportError(f"AgentHubClient requires httpx. Install with: pip install httpx\nOriginal error: {e}")
    _optional_imports['AgentHubClient'] = AgentHubClient

try:
    from .registry import register_agent, publish_agent
    _optional_imports['register_agent'] = register_agent
    _optional_imports['publish_agent'] = publish_agent
except ImportError as e:
    def register_agent(*args, **kwargs):
        raise ImportError(f"register_agent requires PyYAML. Install with: pip install pyyaml\nOriginal error: {e}")
    def publish_agent(*args, **kwargs):
        raise ImportError(f"publish_agent requires PyYAML. Install with: pip install pyyaml\nOriginal error: {e}")
    _optional_imports['register_agent'] = register_agent
    _optional_imports['publish_agent'] = publish_agent

try:
    from .server import serve_agent
    _optional_imports['serve_agent'] = serve_agent
except ImportError as e:
    def serve_agent(*args, **kwargs):
        raise ImportError(f"serve_agent requires uvicorn. Install with: pip install uvicorn\nOriginal error: {e}")
    _optional_imports['serve_agent'] = serve_agent

# Export all available functions
AgentBuilder = _optional_imports['AgentBuilder']
AgentHubClient = _optional_imports['AgentHubClient']
register_agent = _optional_imports['register_agent']
publish_agent = _optional_imports['publish_agent']
serve_agent = _optional_imports['serve_agent']

__all__ = [
    "AgentBuilder",
    "AgentHubClient", 
    "AgentMetadata",
    "PricingModel",
    "AgentEndpoint",
    "endpoint",
    "expose",
    "register_agent",
    "publish_agent",
    "serve_agent",
]

# Utility function to check what's available
def check_dependencies():
    """Check which dependencies are available"""
    status = {
        "core": True,  # Always available
        "fastapi": False,
        "httpx": False,
        "pyyaml": False,
        "uvicorn": False,
        "rich": False,
        "click": False
    }
    
    try:
        import fastapi
        status["fastapi"] = True
    except ImportError:
        pass
    
    try:
        import httpx
        status["httpx"] = True
    except ImportError:
        pass
    
    try:
        import yaml
        status["pyyaml"] = True
    except ImportError:
        pass
    
    try:
        import uvicorn
        status["uvicorn"] = True
    except ImportError:
        pass
    
    try:
        import rich
        status["rich"] = True
    except ImportError:
        pass
    
    try:
        import click
        status["click"] = True
    except ImportError:
        pass
    
    return status