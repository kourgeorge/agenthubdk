"""
AgentHub Client - For interacting with the AgentHub API
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List, Union
import json
import time
from .models import (
    AgentMetadata, TaskRequest, TaskResponse, AgentStatus, 
    AgentRegistration, PricingModel
)


class AgentHubClient:
    """
    Client for interacting with the AgentHub API.
    
    This client allows you to:
    - Search and discover agents
    - Hire agents to perform tasks
    - Monitor agent status and performance
    - Manage billing and credits
    
    Example:
        client = AgentHubClient(api_key="your-api-key")
        
        # Search for agents
        agents = client.search_agents(category="research")
        
        # Hire an agent
        result = client.hire_agent(
            agent_id="research-agent-123",
            endpoint="/query",
            parameters={"question": "What is AI?"}
        )
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://api.agenthub.ai",
        timeout: int = 30
    ):
        """
        Initialize the AgentHub client.
        
        Args:
            api_key: Your AgentHub API key
            base_url: AgentHub API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AgentHub-Python-SDK/0.1.0"
        }
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a synchronous HTTP request to the AgentHub API"""
        url = f"{self.base_url}{endpoint}"
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def _make_async_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an asynchronous HTTP request to the AgentHub API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    def search_agents(
        self, 
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_reliability: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for agents in the AgentHub marketplace.
        
        Args:
            category: Filter by category
            tags: Filter by tags
            min_reliability: Minimum reliability score (0-100)
            max_price: Maximum price per request
            limit: Maximum number of results
            
        Returns:
            List of agent information dictionaries
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        if tags:
            params["tags"] = ",".join(tags)
        if min_reliability is not None:
            params["min_reliability"] = min_reliability
        if max_price is not None:
            params["max_price"] = max_price
            
        return self._make_request("GET", "/agents", params=params)
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Agent information dictionary
        """
        return self._make_request("GET", f"/agents/{agent_id}")
    
    def hire_agent(
        self, 
        agent_id: str, 
        endpoint: str, 
        parameters: Dict[str, Any],
        timeout: Optional[int] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hire an agent to perform a task.
        
        Args:
            agent_id: The agent ID to hire
            endpoint: The agent endpoint to call
            parameters: Parameters to send to the agent
            timeout: Task timeout in seconds
            callback_url: URL for async result callback
            
        Returns:
            Task result dictionary
        """
        task_data = {
            "agent_id": agent_id,
            "endpoint": endpoint,
            "parameters": parameters
        }
        
        if timeout:
            task_data["timeout"] = timeout
        if callback_url:
            task_data["callback_url"] = callback_url
            
        return self._make_request("POST", "/tasks", data=task_data)
    
    async def hire_agent_async(
        self, 
        agent_id: str, 
        endpoint: str, 
        parameters: Dict[str, Any],
        timeout: Optional[int] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hire an agent asynchronously.
        
        Args:
            agent_id: The agent ID to hire
            endpoint: The agent endpoint to call
            parameters: Parameters to send to the agent
            timeout: Task timeout in seconds
            callback_url: URL for async result callback
            
        Returns:
            Task result dictionary
        """
        task_data = {
            "agent_id": agent_id,
            "endpoint": endpoint,
            "parameters": parameters
        }
        
        if timeout:
            task_data["timeout"] = timeout
        if callback_url:
            task_data["callback_url"] = callback_url
            
        return await self._make_async_request("POST", "/tasks", data=task_data)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task status dictionary
        """
        return self._make_request("GET", f"/tasks/{task_id}")
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance and usage information.
        
        Returns:
            Account balance dictionary
        """
        return self._make_request("GET", "/account/balance")
    
    def get_usage_history(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get usage history.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of records
            
        Returns:
            List of usage records
        """
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        return self._make_request("GET", "/account/usage", params=params)
    
    def register_agent(self, agent_metadata: AgentMetadata) -> Dict[str, Any]:
        """
        Register a new agent (requires Creator API key).
        
        Args:
            agent_metadata: Agent metadata
            
        Returns:
            Registration result dictionary
        """
        registration_data = {
            "metadata": agent_metadata.dict(),
            "api_key": self.api_key
        }
        
        return self._make_request("POST", "/agents/register", data=registration_data)
    
    def update_agent(self, agent_id: str, agent_metadata: AgentMetadata) -> Dict[str, Any]:
        """
        Update an existing agent (requires Creator API key).
        
        Args:
            agent_id: Agent ID to update
            agent_metadata: Updated agent metadata
            
        Returns:
            Update result dictionary
        """
        update_data = {
            "metadata": agent_metadata.dict(),
            "api_key": self.api_key
        }
        
        return self._make_request("PUT", f"/agents/{agent_id}", data=update_data)
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Delete an agent (requires Creator API key).
        
        Args:
            agent_id: Agent ID to delete
            
        Returns:
            Deletion result dictionary
        """
        return self._make_request("DELETE", f"/agents/{agent_id}")
    
    def get_agent_analytics(self, agent_id: str) -> Dict[str, Any]:
        """
        Get analytics for an agent (requires Creator API key).
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent analytics dictionary
        """
        return self._make_request("GET", f"/agents/{agent_id}/analytics")
    
    def batch_hire_agents(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hire multiple agents in a single request.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            List of task results
        """
        return self._make_request("POST", "/tasks/batch", data={"tasks": tasks})
    
    async def batch_hire_agents_async(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hire multiple agents asynchronously.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            List of task results
        """
        return await self._make_async_request("POST", "/tasks/batch", data={"tasks": tasks})


class AgentHubClientError(Exception):
    """Base exception for AgentHub client errors"""
    pass


class AuthenticationError(AgentHubClientError):
    """Authentication error"""
    pass


class AgentNotFoundError(AgentHubClientError):
    """Agent not found error"""
    pass


class InsufficientCreditsError(AgentHubClientError):
    """Insufficient credits error"""
    pass


class TaskTimeoutError(AgentHubClientError):
    """Task timeout error"""
    pass