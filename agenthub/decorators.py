"""
Decorators for AgentHub SDK
"""

from typing import Dict, Any, Callable, Optional
from functools import wraps


def endpoint(path: str, method: str = "POST", description: str = ""):
    """
    Decorator to mark a function as an agent endpoint.
    
    This is a standalone decorator that can be used when not using AgentBuilder.
    
    Args:
        path: The endpoint path
        method: HTTP method 
        description: Endpoint description
        
    Example:
        @endpoint("/process", description="Process data")
        def process_data(request):
            return {"result": "processed"}
    """
    def decorator(func: Callable):
        # Add endpoint metadata to the function
        func._agenthub_endpoint = {
            "path": path,
            "method": method,
            "description": description
        }
        return func
    return decorator


def expose(func: Callable):
    """
    Decorator to expose a function as an agent capability.
    
    This is a simpler decorator for quick capability exposure.
    
    Args:
        func: Function to expose
        
    Example:
        @expose
        def search_web(query: str) -> str:
            return f"Search results for {query}"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    # Add exposure metadata
    wrapper._agenthub_exposed = True
    wrapper._agenthub_name = func.__name__
    wrapper._agenthub_description = func.__doc__ or f"Exposed function: {func.__name__}"
    
    return wrapper


def capability(name: str, description: str = "", parameters: Dict[str, Any] = None):
    """
    Decorator to mark a function as an agent capability with metadata.
    
    Args:
        name: Capability name
        description: Capability description
        parameters: Expected parameters schema
        
    Example:
        @capability("web_search", "Search the web", {"query": {"type": "string"}})
        def search_web(query: str) -> str:
            return f"Search results for {query}"
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Add capability metadata
        wrapper._agenthub_capability = {
            "name": name,
            "description": description or func.__doc__ or f"Capability: {name}",
            "parameters": parameters or {}
        }
        
        return wrapper
    return decorator


def async_endpoint(path: str, method: str = "POST", description: str = ""):
    """
    Decorator for async endpoints.
    
    Args:
        path: The endpoint path
        method: HTTP method
        description: Endpoint description
        
    Example:
        @async_endpoint("/async_process")
        async def process_async(request):
            await asyncio.sleep(1)
            return {"result": "processed"}
    """
    def decorator(func: Callable):
        # Add endpoint metadata
        func._agenthub_endpoint = {
            "path": path,
            "method": method,
            "description": description,
            "async": True
        }
        return func
    return decorator


def validate_request(schema: Dict[str, Any]):
    """
    Decorator to validate request data against a schema.
    
    Args:
        schema: JSON schema for request validation
        
    Example:
        @validate_request({"query": {"type": "string", "required": True}})
        @endpoint("/search")
        def search(request):
            return {"results": []}
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Basic validation (can be extended with jsonschema)
            if hasattr(request, 'json') and request.json:
                data = request.json
                for field, field_schema in schema.items():
                    if field_schema.get("required", False) and field not in data:
                        raise ValueError(f"Required field '{field}' missing")
            
            return func(request, *args, **kwargs)
        
        # Add validation metadata
        wrapper._agenthub_validation = schema
        return wrapper
    return decorator


def rate_limit(calls_per_minute: int = 60):
    """
    Decorator to add rate limiting to endpoints.
    
    Args:
        calls_per_minute: Maximum calls per minute
        
    Example:
        @rate_limit(30)
        @endpoint("/expensive_operation")
        def expensive_op(request):
            return {"result": "done"}
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Rate limiting logic would go here
            # For now, just add metadata
            return func(*args, **kwargs)
        
        # Add rate limiting metadata
        wrapper._agenthub_rate_limit = calls_per_minute
        return wrapper
    return decorator


def require_auth(func: Callable):
    """
    Decorator to require authentication for an endpoint.
    
    Example:
        @require_auth
        @endpoint("/admin")
        def admin_endpoint(request):
            return {"admin": "data"}
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Authentication logic would go here
        # For now, just add metadata
        return func(request, *args, **kwargs)
    
    # Add auth metadata
    wrapper._agenthub_requires_auth = True
    return wrapper


def cache_result(ttl_seconds: int = 300):
    """
    Decorator to cache endpoint results.
    
    Args:
        ttl_seconds: Cache time-to-live in seconds
        
    Example:
        @cache_result(600)
        @endpoint("/expensive_query")
        def expensive_query(request):
            return {"result": "expensive computation"}
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Caching logic would go here
            return func(*args, **kwargs)
        
        # Add caching metadata
        wrapper._agenthub_cache_ttl = ttl_seconds
        return wrapper
    return decorator