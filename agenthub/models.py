"""
Pydantic models for AgentHub SDK
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class PricingType(str, Enum):
    """Pricing model types for agents"""
    FIXED = "fixed"
    PER_REQUEST = "per_request"
    PER_TOKEN = "per_token"
    PER_MINUTE = "per_minute"


class AgentProtocol(str, Enum):
    """Supported agent communication protocols"""
    ACP = "ACP"  # Agent Communication Protocol
    MCP = "MCP"  # Model Context Protocol
    HTTP = "HTTP"  # Standard HTTP REST API


class AgentRuntime(str, Enum):
    """Agent runtime environments"""
    EXTERNAL = "external"
    MANAGED = "managed"
    SERVERLESS = "serverless"


class PricingModel(BaseModel):
    """Pricing configuration for an agent"""
    type: PricingType = Field(..., description="The pricing model type")
    price: float = Field(..., ge=0, description="Price per unit")
    currency: str = Field(default="USD", description="Currency code")
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v


class AgentCapability(BaseModel):
    """Individual agent capability description"""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Expected parameters")


class AgentEndpoint(BaseModel):
    """Agent endpoint configuration"""
    path: str = Field(..., description="Endpoint path")
    method: str = Field(default="POST", description="HTTP method")
    description: str = Field(..., description="Endpoint description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Expected parameters")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="Response schema")


class AgentMetadata(BaseModel):
    """Complete agent metadata"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    version: str = Field(default="1.0.0", description="Agent version")
    category: str = Field(..., description="Agent category")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    endpoints: List[AgentEndpoint] = Field(default_factory=list, description="Agent endpoints")
    pricing: PricingModel = Field(..., description="Pricing model")
    protocol: AgentProtocol = Field(default=AgentProtocol.ACP, description="Communication protocol")
    runtime: AgentRuntime = Field(default=AgentRuntime.EXTERNAL, description="Runtime environment")
    endpoint_url: Optional[str] = Field(None, description="External endpoint URL")
    requirements: List[str] = Field(default_factory=list, description="Runtime requirements")
    author: Optional[str] = Field(None, description="Agent author")
    license: Optional[str] = Field(None, description="Agent license")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Agent name cannot be empty")
        return v.strip()
    
    @validator('version')
    def validate_version(cls, v):
        # Basic semantic versioning validation
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError("Version must be in format X.Y.Z")
        for part in parts:
            if not part.isdigit():
                raise ValueError("Version parts must be numeric")
        return v


class TaskRequest(BaseModel):
    """Task request from client to agent"""
    agent_id: str = Field(..., description="Target agent ID")
    endpoint: str = Field(..., description="Target endpoint")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    callback_url: Optional[str] = Field(None, description="Callback URL for async results")
    timeout: Optional[int] = Field(None, ge=1, description="Timeout in seconds")
    priority: int = Field(default=0, ge=0, le=10, description="Task priority (0-10)")


class TaskResponse(BaseModel):
    """Task response from agent to client"""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    cost: Optional[float] = Field(None, description="Task cost")


class AgentRegistration(BaseModel):
    """Agent registration request"""
    metadata: AgentMetadata = Field(..., description="Agent metadata")
    api_key: str = Field(..., description="Creator API key")
    
    class Config:
        # Hide API key in string representation
        repr_exclude = {"api_key"}


class AgentStatus(BaseModel):
    """Agent status information"""
    agent_id: str = Field(..., description="Agent ID")
    status: str = Field(..., description="Agent status")
    last_seen: Optional[str] = Field(None, description="Last seen timestamp")
    reliability_score: Optional[float] = Field(None, ge=0, le=100, description="Reliability score")
    total_tasks: int = Field(default=0, description="Total tasks completed")
    success_rate: Optional[float] = Field(None, ge=0, le=1, description="Success rate")
    average_response_time: Optional[float] = Field(None, description="Average response time")