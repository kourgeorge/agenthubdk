"""
Agent Registry - Functions for registering and publishing agents
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from .client import AgentHubClient
from .models import AgentMetadata, PricingModel, AgentRegistration
from .agent_builder import AgentBuilder
import logging

logger = logging.getLogger(__name__)


def register_agent(
    agent: AgentBuilder, 
    api_key: Optional[str] = None,
    config_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Register an agent with the AgentHub registry.
    
    Args:
        agent: AgentBuilder instance
        api_key: Creator API key (can also be set via environment variable)
        config_file: Path to configuration file
        
    Returns:
        Registration result dictionary
        
    Example:
        result = register_agent(agent, api_key="your-creator-key")
    """
    # Get API key from various sources
    if not api_key:
        api_key = os.getenv("AGENTHUB_API_KEY")
        if not api_key and config_file:
            config = _load_config(config_file)
            api_key = config.get("api_key")
    
    if not api_key:
        raise ValueError("API key is required. Set AGENTHUB_API_KEY environment variable or pass api_key parameter.")
    
    # Validate agent
    agent.validate()
    
    # Create client and register
    client = AgentHubClient(api_key=api_key)
    return client.register_agent(agent.get_metadata())


def publish_agent(
    agent: AgentBuilder, 
    api_key: Optional[str] = None,
    config_file: Optional[str] = None,
    endpoint_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publish an agent to the AgentHub marketplace.
    
    This is a convenience function that combines registration and publishing.
    
    Args:
        agent: AgentBuilder instance
        api_key: Creator API key
        config_file: Path to configuration file
        endpoint_url: External endpoint URL for the agent
        
    Returns:
        Publication result dictionary
        
    Example:
        result = publish_agent(
            agent, 
            api_key="your-creator-key",
            endpoint_url="https://your-domain.com/agent"
        )
    """
    # Set endpoint URL if provided
    if endpoint_url and agent.get_metadata():
        agent.get_metadata().endpoint_url = endpoint_url
    
    # Register the agent
    registration_result = register_agent(agent, api_key, config_file)
    
    logger.info(f"Agent published successfully: {registration_result}")
    return registration_result


def create_agent_from_yaml(yaml_file: str) -> AgentBuilder:
    """
    Create an AgentBuilder instance from a YAML configuration file.
    
    Args:
        yaml_file: Path to YAML configuration file
        
    Returns:
        AgentBuilder instance
        
    Example YAML:
        name: my-agent
        description: My awesome agent
        category: research
        pricing:
          type: per_request
          price: 0.05
        endpoints:
          - path: /query
            description: Process queries
    """
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    
    agent = AgentBuilder(config['name'])
    
    # Set metadata
    metadata = {
        "name": config['name'],
        "description": config.get('description', ''),
        "category": config.get('category', 'general'),
        "version": config.get('version', '1.0.0'),
        "tags": config.get('tags', []),
        "pricing": config.get('pricing', {"type": "per_request", "price": 0.01})
    }
    
    # Add optional fields
    for field in ['author', 'license', 'documentation_url', 'repository_url']:
        if field in config:
            metadata[field] = config[field]
    
    agent.set_metadata(metadata)
    
    return agent


def create_agent_from_json(json_file: str) -> AgentBuilder:
    """
    Create an AgentBuilder instance from a JSON configuration file.
    
    Args:
        json_file: Path to JSON configuration file
        
    Returns:
        AgentBuilder instance
    """
    with open(json_file, 'r') as f:
        config = json.load(f)
    
    agent = AgentBuilder(config['name'])
    
    # Set metadata
    metadata = {
        "name": config['name'],
        "description": config.get('description', ''),
        "category": config.get('category', 'general'),
        "version": config.get('version', '1.0.0'),
        "tags": config.get('tags', []),
        "pricing": config.get('pricing', {"type": "per_request", "price": 0.01})
    }
    
    # Add optional fields
    for field in ['author', 'license', 'documentation_url', 'repository_url']:
        if field in config:
            metadata[field] = config[field]
    
    agent.set_metadata(metadata)
    
    return agent


def update_agent_metadata(
    agent_id: str,
    metadata: Dict[str, Any],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update agent metadata in the registry.
    
    Args:
        agent_id: Agent ID to update
        metadata: Updated metadata
        api_key: Creator API key
        
    Returns:
        Update result dictionary
    """
    if not api_key:
        api_key = os.getenv("AGENTHUB_API_KEY")
    
    if not api_key:
        raise ValueError("API key is required")
    
    # Convert to AgentMetadata
    agent_metadata = AgentMetadata(**metadata)
    
    # Create client and update
    client = AgentHubClient(api_key=api_key)
    return client.update_agent(agent_id, agent_metadata)


def delete_agent_from_registry(
    agent_id: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete an agent from the registry.
    
    Args:
        agent_id: Agent ID to delete
        api_key: Creator API key
        
    Returns:
        Deletion result dictionary
    """
    if not api_key:
        api_key = os.getenv("AGENTHUB_API_KEY")
    
    if not api_key:
        raise ValueError("API key is required")
    
    # Create client and delete
    client = AgentHubClient(api_key=api_key)
    return client.delete_agent(agent_id)


def get_agent_status(
    agent_id: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get agent status from the registry.
    
    Args:
        agent_id: Agent ID
        api_key: Creator API key
        
    Returns:
        Agent status dictionary
    """
    if not api_key:
        api_key = os.getenv("AGENTHUB_API_KEY")
    
    if not api_key:
        raise ValueError("API key is required")
    
    # Create client and get status
    client = AgentHubClient(api_key=api_key)
    return client.get_agent(agent_id)


def _load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from file"""
    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    elif config_file.endswith('.json'):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        raise ValueError("Config file must be YAML or JSON")


def validate_agent_config(config: Dict[str, Any]) -> bool:
    """
    Validate agent configuration.
    
    Args:
        config: Agent configuration dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ['name', 'description', 'category', 'pricing']
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Required field '{field}' missing from config")
    
    # Validate pricing
    pricing = config['pricing']
    if not isinstance(pricing, dict):
        raise ValueError("Pricing must be a dictionary")
    
    if 'type' not in pricing or 'price' not in pricing:
        raise ValueError("Pricing must include 'type' and 'price'")
    
    valid_pricing_types = ['fixed', 'per_request', 'per_token', 'per_minute']
    if pricing['type'] not in valid_pricing_types:
        raise ValueError(f"Pricing type must be one of {valid_pricing_types}")
    
    if not isinstance(pricing['price'], (int, float)) or pricing['price'] < 0:
        raise ValueError("Pricing price must be a non-negative number")
    
    return True


def generate_agent_template(
    name: str,
    output_file: str = "agent_config.yaml",
    format: str = "yaml"
) -> str:
    """
    Generate an agent configuration template.
    
    Args:
        name: Agent name
        output_file: Output file path
        format: Output format ('yaml' or 'json')
        
    Returns:
        Path to generated file
    """
    template = {
        "name": name,
        "description": f"Description for {name}",
        "category": "general",
        "version": "1.0.0",
        "tags": [],
        "pricing": {
            "type": "per_request",
            "price": 0.01,
            "currency": "USD"
        },
        "author": "Your Name",
        "license": "MIT",
        "documentation_url": "",
        "repository_url": ""
    }
    
    if format.lower() == 'yaml':
        with open(output_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False)
    elif format.lower() == 'json':
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2)
    else:
        raise ValueError("Format must be 'yaml' or 'json'")
    
    return output_file