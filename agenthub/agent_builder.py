"""
AgentBuilder - Core class for creating and configuring AgentHub agents
"""

from typing import Dict, Any, Optional, List, Callable, Union
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uuid
import time
import logging
from .models import (
    AgentMetadata, PricingModel, AgentEndpoint, AgentCapability,
    TaskRequest, TaskResponse, PricingType, AgentProtocol, AgentRuntime
)

logger = logging.getLogger(__name__)


class AgentBuilder:
    """
    Main class for building and configuring AgentHub agents.
    
    Example:
        agent = AgentBuilder("my-agent")
        
        @agent.endpoint("/process")
        def process_data(request):
            return {"result": "processed"}
            
        agent.set_metadata({
            "name": "My Agent",
            "description": "Does amazing things",
            "category": "utility"
        })
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize the AgentBuilder.
        
        Args:
            agent_name: Unique name for the agent
        """
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())
        self.app = FastAPI(title=f"AgentHub Agent: {agent_name}")
        self.endpoints: Dict[str, Dict[str, Any]] = {}
        self.metadata: Optional[AgentMetadata] = None
        self._setup_default_endpoints()
        
    def _setup_default_endpoints(self):
        """Setup default health and info endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "agent_id": self.agent_id}
            
        @self.app.get("/info")
        async def agent_info():
            """Agent information endpoint"""
            return {
                "agent_id": self.agent_id,
                "name": self.agent_name,
                "metadata": self.metadata.dict() if self.metadata else None,
                "endpoints": list(self.endpoints.keys())
            }
    
    def endpoint(self, path: str, method: str = "POST", description: str = ""):
        """
        Decorator to register an endpoint with the agent.
        
        Args:
            path: The endpoint path (e.g., "/process")
            method: HTTP method (default: POST)
            description: Endpoint description
            
        Example:
            @agent.endpoint("/query", description="Process queries")
            def handle_query(request):
                return {"result": "processed"}
        """
        def decorator(func: Callable):
            # Register the endpoint
            self.endpoints[path] = {
                "function": func,
                "method": method,
                "description": description,
                "path": path
            }
            
            # Add to FastAPI app
            if method.upper() == "GET":
                self.app.get(path)(self._wrap_endpoint_function(func, path))
            elif method.upper() == "POST":
                self.app.post(path)(self._wrap_endpoint_function(func, path))
            elif method.upper() == "PUT":
                self.app.put(path)(self._wrap_endpoint_function(func, path))
            elif method.upper() == "DELETE":
                self.app.delete(path)(self._wrap_endpoint_function(func, path))
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return func
        return decorator
    
    def _wrap_endpoint_function(self, func: Callable, path: str):
        """Wrap user function with AgentHub protocol handling"""
        async def wrapper(request: Request):
            try:
                start_time = time.time()
                
                # Parse request
                if request.method in ["POST", "PUT"]:
                    try:
                        body = await request.json()
                    except:
                        body = {}
                else:
                    body = dict(request.query_params)
                
                # Create enhanced request object
                enhanced_request = type('Request', (), {
                    'json': body,
                    'query_params': dict(request.query_params),
                    'headers': dict(request.headers),
                    'method': request.method,
                    'url': str(request.url),
                    'path': path
                })()
                
                # Call user function
                result = func(enhanced_request)
                
                # Handle async functions
                if hasattr(result, '__await__'):
                    result = await result
                
                execution_time = time.time() - start_time
                
                # Wrap result in AgentHub protocol
                response = {
                    "agent_id": self.agent_id,
                    "endpoint": path,
                    "result": result,
                    "execution_time": execution_time,
                    "status": "success",
                    "timestamp": time.time()
                }
                
                return JSONResponse(content=response)
                
            except Exception as e:
                logger.error(f"Error in endpoint {path}: {str(e)}")
                execution_time = time.time() - start_time
                
                error_response = {
                    "agent_id": self.agent_id,
                    "endpoint": path,
                    "error": str(e),
                    "execution_time": execution_time,
                    "status": "error",
                    "timestamp": time.time()
                }
                
                return JSONResponse(content=error_response, status_code=500)
        
        return wrapper
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """
        Set agent metadata.
        
        Args:
            metadata: Dictionary containing agent metadata
            
        Example:
            agent.set_metadata({
                "name": "Research Assistant",
                "description": "AI agent for research tasks",
                "category": "research",
                "pricing": {"type": "per_request", "price": 0.05}
            })
        """
        # Handle pricing model
        if "pricing" in metadata:
            pricing_data = metadata["pricing"]
            if isinstance(pricing_data, dict):
                metadata["pricing"] = PricingModel(**pricing_data)
        
        # Convert endpoints to AgentEndpoint objects
        endpoints = []
        for path, endpoint_data in self.endpoints.items():
            endpoints.append(AgentEndpoint(
                path=path,
                method=endpoint_data["method"],
                description=endpoint_data["description"]
            ))
        
        metadata["endpoints"] = endpoints
        
        # Create AgentMetadata object
        self.metadata = AgentMetadata(**metadata)
        
    def add_capability(self, name: str, description: str, parameters: Dict[str, Any] = None):
        """
        Add a capability to the agent.
        
        Args:
            name: Capability name
            description: Capability description
            parameters: Expected parameters
        """
        if not self.metadata:
            raise ValueError("Must set metadata before adding capabilities")
            
        capability = AgentCapability(
            name=name,
            description=description,
            parameters=parameters or {}
        )
        
        self.metadata.capabilities.append(capability)
    
    def set_pricing(self, pricing_type: Union[str, PricingType], price: float, currency: str = "USD"):
        """
        Set pricing model for the agent.
        
        Args:
            pricing_type: Type of pricing (fixed, per_request, per_token, per_minute)
            price: Price per unit
            currency: Currency code
        """
        if isinstance(pricing_type, str):
            pricing_type = PricingType(pricing_type)
            
        pricing_model = PricingModel(
            type=pricing_type,
            price=price,
            currency=currency
        )
        
        if self.metadata:
            self.metadata.pricing = pricing_model
        else:
            # Store for later use
            self._pending_pricing = pricing_model
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance"""
        return self.app
    
    def get_metadata(self) -> Optional[AgentMetadata]:
        """Get the agent metadata"""
        return self.metadata
    
    def get_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Get registered endpoints"""
        return self.endpoints
    
    def validate(self) -> bool:
        """
        Validate the agent configuration.
        
        Returns:
            True if valid, raises ValueError if invalid
        """
        if not self.metadata:
            raise ValueError("Agent metadata must be set")
            
        if not self.endpoints:
            raise ValueError("Agent must have at least one endpoint")
            
        return True


# Convenience function for backward compatibility
def Agent(name: str) -> AgentBuilder:
    """
    Create an AgentBuilder instance.
    
    Args:
        name: Agent name
        
    Returns:
        AgentBuilder instance
    """
    return AgentBuilder(name)