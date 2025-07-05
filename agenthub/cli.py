"""
AgentHub CLI - Command-line interface for AgentHub SDK
"""

import click
import os
import sys
import json
import yaml
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text

from .client import AgentHubClient
from .registry import (
    register_agent, publish_agent, create_agent_from_yaml, 
    create_agent_from_json, generate_agent_template
)
from .server import serve_agent, run_agent_from_config
from .agent_builder import AgentBuilder

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """AgentHub SDK - CLI for managing AI agents"""
    pass


@main.command()
@click.option('--name', required=True, help='Agent name')
@click.option('--format', default='yaml', help='Config format (yaml/json)')
@click.option('--output', default='agent_config.yaml', help='Output file')
def init(name: str, format: str, output: str):
    """Initialize a new agent configuration"""
    try:
        config_file = generate_agent_template(name, output, format)
        console.print(f"✅ Created agent configuration: {config_file}", style="green")
        console.print(f"📝 Edit {config_file} to configure your agent", style="blue")
    except Exception as e:
        console.print(f"❌ Error creating configuration: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--config', required=True, help='Agent configuration file')
@click.option('--api-key', help='Creator API key (or set AGENTHUB_API_KEY)')
@click.option('--endpoint-url', help='External endpoint URL')
def register(config: str, api_key: Optional[str], endpoint_url: Optional[str]):
    """Register an agent with AgentHub"""
    try:
        # Load agent from config
        if config.endswith('.yaml') or config.endswith('.yml'):
            agent = create_agent_from_yaml(config)
        elif config.endswith('.json'):
            agent = create_agent_from_json(config)
        else:
            console.print("❌ Config file must be YAML or JSON", style="red")
            sys.exit(1)
        
        # Set endpoint URL if provided
        if endpoint_url:
            agent.get_metadata().endpoint_url = endpoint_url
        
        # Register agent
        with console.status("Registering agent..."):
            result = register_agent(agent, api_key)
        
        console.print("✅ Agent registered successfully!", style="green")
        console.print(f"🆔 Agent ID: {result.get('agent_id', 'N/A')}")
        console.print(f"🔗 Dashboard: {result.get('dashboard_url', 'N/A')}")
        
    except Exception as e:
        console.print(f"❌ Error registering agent: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--config', required=True, help='Agent configuration file')
@click.option('--api-key', help='Creator API key (or set AGENTHUB_API_KEY)')
@click.option('--endpoint-url', help='External endpoint URL')
def publish(config: str, api_key: Optional[str], endpoint_url: Optional[str]):
    """Publish an agent to AgentHub marketplace"""
    try:
        # Load agent from config
        if config.endswith('.yaml') or config.endswith('.yml'):
            agent = create_agent_from_yaml(config)
        elif config.endswith('.json'):
            agent = create_agent_from_json(config)
        else:
            console.print("❌ Config file must be YAML or JSON", style="red")
            sys.exit(1)
        
        # Publish agent
        with console.status("Publishing agent..."):
            result = publish_agent(agent, api_key, endpoint_url=endpoint_url)
        
        console.print("✅ Agent published successfully!", style="green")
        console.print(f"🆔 Agent ID: {result.get('agent_id', 'N/A')}")
        console.print(f"🔗 Marketplace: {result.get('marketplace_url', 'N/A')}")
        
    except Exception as e:
        console.print(f"❌ Error publishing agent: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--config', required=True, help='Agent configuration file')
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(config: str, host: str, port: int, reload: bool):
    """Serve an agent locally"""
    try:
        console.print(f"🚀 Starting agent server on {host}:{port}", style="blue")
        if reload:
            console.print("🔄 Auto-reload enabled", style="yellow")
        
        run_agent_from_config(config, host=host, port=port, reload=reload)
        
    except Exception as e:
        console.print(f"❌ Error starting server: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--config', required=True, help='Agent configuration file')
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
def dev(config: str, host: str, port: int):
    """Start development server with auto-reload"""
    try:
        console.print(f"🧪 Starting development server on {host}:{port}", style="blue")
        console.print("🔄 Auto-reload and debug mode enabled", style="yellow")
        
        run_agent_from_config(config, host=host, port=port, reload=True, log_level="debug")
        
    except Exception as e:
        console.print(f"❌ Error starting development server: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--api-key', help='Client API key (or set AGENTHUB_API_KEY)')
@click.option('--category', help='Filter by category')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--limit', default=10, help='Maximum number of results')
def search(api_key: Optional[str], category: Optional[str], tags: Optional[str], limit: int):
    """Search for agents in the marketplace"""
    try:
        if not api_key:
            api_key = os.getenv("AGENTHUB_API_KEY")
        
        if not api_key:
            console.print("❌ API key required", style="red")
            sys.exit(1)
        
        client = AgentHubClient(api_key=api_key)
        
        # Parse tags
        tag_list = tags.split(',') if tags else None
        
        with console.status("Searching agents..."):
            agents = client.search_agents(
                category=category,
                tags=tag_list,
                limit=limit
            )
        
        if not agents:
            console.print("No agents found matching your criteria", style="yellow")
            return
        
        # Display results in a table
        table = Table(title="Available Agents")
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Price", style="green")
        table.add_column("Rating", style="yellow")
        table.add_column("Description", style="white")
        
        for agent in agents:
            table.add_row(
                agent.get('name', 'N/A'),
                agent.get('category', 'N/A'),
                f"${agent.get('price', 0):.3f}",
                f"{agent.get('rating', 0):.1f}/5",
                agent.get('description', 'N/A')[:50] + "..."
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error searching agents: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.argument('agent_id')
@click.option('--api-key', help='Client API key (or set AGENTHUB_API_KEY)')
def info(agent_id: str, api_key: Optional[str]):
    """Get detailed information about an agent"""
    try:
        if not api_key:
            api_key = os.getenv("AGENTHUB_API_KEY")
        
        if not api_key:
            console.print("❌ API key required", style="red")
            sys.exit(1)
        
        client = AgentHubClient(api_key=api_key)
        
        with console.status("Getting agent information..."):
            agent = client.get_agent(agent_id)
        
        # Display agent information
        console.print(Panel(f"Agent: {agent.get('name', 'N/A')}", style="blue"))
        console.print(f"🆔 ID: {agent.get('id', 'N/A')}")
        console.print(f"📝 Description: {agent.get('description', 'N/A')}")
        console.print(f"🏷️ Category: {agent.get('category', 'N/A')}")
        console.print(f"💰 Price: ${agent.get('price', 0):.3f}")
        console.print(f"⭐ Rating: {agent.get('rating', 0):.1f}/5")
        console.print(f"📊 Reliability: {agent.get('reliability_score', 0):.1f}%")
        console.print(f"🔗 Endpoint: {agent.get('endpoint_url', 'N/A')}")
        
        # Display endpoints
        endpoints = agent.get('endpoints', [])
        if endpoints:
            console.print("\n📡 Available Endpoints:")
            for endpoint in endpoints:
                console.print(f"  • {endpoint.get('method', 'POST')} {endpoint.get('path', 'N/A')}")
                console.print(f"    {endpoint.get('description', 'No description')}")
        
    except Exception as e:
        console.print(f"❌ Error getting agent info: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.argument('agent_id')
@click.argument('endpoint')
@click.option('--api-key', help='Client API key (or set AGENTHUB_API_KEY)')
@click.option('--params', help='Parameters as JSON string')
@click.option('--timeout', type=int, help='Request timeout in seconds')
def hire(agent_id: str, endpoint: str, api_key: Optional[str], params: Optional[str], timeout: Optional[int]):
    """Hire an agent to perform a task"""
    try:
        if not api_key:
            api_key = os.getenv("AGENTHUB_API_KEY")
        
        if not api_key:
            console.print("❌ API key required", style="red")
            sys.exit(1)
        
        client = AgentHubClient(api_key=api_key)
        
        # Parse parameters
        parameters = {}
        if params:
            try:
                parameters = json.loads(params)
            except json.JSONDecodeError:
                console.print("❌ Invalid JSON parameters", style="red")
                sys.exit(1)
        
        with console.status("Hiring agent..."):
            result = client.hire_agent(
                agent_id=agent_id,
                endpoint=endpoint,
                parameters=parameters,
                timeout=timeout
            )
        
        console.print("✅ Task completed successfully!", style="green")
        console.print(f"🆔 Task ID: {result.get('task_id', 'N/A')}")
        console.print(f"💰 Cost: ${result.get('cost', 0):.3f}")
        console.print(f"⏱️ Duration: {result.get('execution_time', 0):.2f}s")
        
        # Display result
        if 'result' in result:
            console.print("\n📊 Result:")
            console.print(json.dumps(result['result'], indent=2))
        
    except Exception as e:
        console.print(f"❌ Error hiring agent: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--api-key', help='Client API key (or set AGENTHUB_API_KEY)')
def balance(api_key: Optional[str]):
    """Check account balance"""
    try:
        if not api_key:
            api_key = os.getenv("AGENTHUB_API_KEY")
        
        if not api_key:
            console.print("❌ API key required", style="red")
            sys.exit(1)
        
        client = AgentHubClient(api_key=api_key)
        
        with console.status("Getting account balance..."):
            balance_info = client.get_account_balance()
        
        console.print(Panel("Account Balance", style="blue"))
        console.print(f"💰 Balance: ${balance_info.get('balance', 0):.2f}")
        console.print(f"📊 Usage this month: ${balance_info.get('usage_this_month', 0):.2f}")
        console.print(f"📈 Total usage: ${balance_info.get('total_usage', 0):.2f}")
        
    except Exception as e:
        console.print(f"❌ Error getting balance: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--api-key', help='Client API key (or set AGENTHUB_API_KEY)')
@click.option('--limit', default=10, help='Number of records to show')
def usage(api_key: Optional[str], limit: int):
    """Show usage history"""
    try:
        if not api_key:
            api_key = os.getenv("AGENTHUB_API_KEY")
        
        if not api_key:
            console.print("❌ API key required", style="red")
            sys.exit(1)
        
        client = AgentHubClient(api_key=api_key)
        
        with console.status("Getting usage history..."):
            usage_history = client.get_usage_history(limit=limit)
        
        if not usage_history:
            console.print("No usage history found", style="yellow")
            return
        
        # Display usage in a table
        table = Table(title="Usage History")
        table.add_column("Date", style="cyan")
        table.add_column("Agent", style="magenta")
        table.add_column("Endpoint", style="green")
        table.add_column("Cost", style="yellow")
        table.add_column("Status", style="white")
        
        for record in usage_history:
            table.add_row(
                record.get('date', 'N/A'),
                record.get('agent_name', 'N/A'),
                record.get('endpoint', 'N/A'),
                f"${record.get('cost', 0):.3f}",
                record.get('status', 'N/A')
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error getting usage history: {str(e)}", style="red")
        sys.exit(1)


@main.command()
@click.option('--config', help='Configuration file to validate')
def validate(config: Optional[str]):
    """Validate agent configuration"""
    try:
        if not config:
            # Look for default config files
            for filename in ['agent_config.yaml', 'agent_config.yml', 'agent_config.json']:
                if os.path.exists(filename):
                    config = filename
                    break
        
        if not config:
            console.print("❌ No configuration file found", style="red")
            sys.exit(1)
        
        # Load and validate configuration
        if config.endswith('.yaml') or config.endswith('.yml'):
            agent = create_agent_from_yaml(config)
        elif config.endswith('.json'):
            agent = create_agent_from_json(config)
        else:
            console.print("❌ Config file must be YAML or JSON", style="red")
            sys.exit(1)
        
        # Validate agent
        agent.validate()
        
        console.print("✅ Configuration is valid!", style="green")
        console.print(f"📝 Agent: {agent.get_metadata().name}")
        console.print(f"🏷️ Category: {agent.get_metadata().category}")
        console.print(f"🔗 Endpoints: {len(agent.get_endpoints())}")
        
    except Exception as e:
        console.print(f"❌ Validation error: {str(e)}", style="red")
        sys.exit(1)


if __name__ == '__main__':
    main()