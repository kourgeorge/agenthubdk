# AgentHub Server - ACP Dynamic Agent Hiring

## Overview

AgentHub Server now supports **dynamic agent hiring** using the **Agent Communication Protocol (ACP)**. Instead of requiring agents to run continuously on dedicated servers, agents are now dynamically spawned when tasks are requested and cleaned up when complete.

## Architecture

### Traditional HTTP-based Architecture (Legacy)
```
Client → Hub Server → Pre-running Agent Server → Response
```

### New ACP-based Architecture
```
Client → Hub Server → [Dynamic ACP Agent Creation] → ACP Communication → Response → [Agent Cleanup]
```

## Key Benefits

- **Resource Efficiency**: Agents only consume resources when actively processing tasks
- **Dynamic Scaling**: Spawn multiple instances of the same agent for parallel processing
- **Simplified Deployment**: No need to manage persistent agent servers
- **Automatic Cleanup**: Agents are automatically cleaned up after task completion
- **Protocol Flexibility**: Support for different agent types (CodeAgent, LLMAgent, etc.)

## Agent Types

### ACP Agents (Recommended)
- **CodeAgent**: AI agents with tool access (search, web browsing, etc.)
- **LLMAgent**: Pure language model agents with custom system prompts
- **ToolAgent**: Custom tool-based agents
- **Generic**: Simple text processing agents

### HTTP Agents (Legacy)
- Traditional REST API agents running on dedicated servers
- Still supported for backward compatibility

## Configuration

### ACP Agent Configuration

```yaml
# example_acp_agent.yaml
name: "Health Assistant"
description: "Medical information agent with search capabilities"
category: "healthcare"
version: "1.0.0"
author: "HealthTech Labs"
tags: ["health", "medical", "search"]
pricing:
  type: "per_request"
  price: 0.50
  currency: "USD"

# ACP Configuration (required for ACP agents)
agent_config:
  type: "code_agent"
  name: "health_assistant"
  description: "Medical information assistant"
  model_id: "openai/gpt-4"
  tools: ["DuckDuckGoSearchTool", "VisitWebpageTool"]
  system_prompt: "You are a medical information assistant. Always remind users to consult healthcare professionals."
```

### HTTP Agent Configuration

```yaml
# example_http_agent.yaml
name: "Calculator Agent"
description: "Mathematical computation agent"
category: "utility"
version: "1.0.0"
author: "MathTech Inc"
endpoints:
  - path: "/calculate"
    method: "POST"
    description: "Perform calculations"
```

## Usage

### 1. Start the Hub Server

```bash
# Development mode (no authentication)
python -m agenthub_server.cli serve --port 8080 --no-auth

# Production mode (with authentication)
python -m agenthub_server.cli serve --port 8080 --require-auth
```

### 2. Register ACP Agents

```bash
# Generate example ACP configuration
python -m agenthub_server.cli example-config --deployment-type acp --output my_agent.yaml

# Register the agent
python -m agenthub_server.cli register-agent --config my_agent.yaml --deployment-type acp
```

### 3. Register HTTP Agents (Legacy)

```bash
# Generate example HTTP configuration
python -m agenthub_server.cli example-config --deployment-type http --output my_http_agent.yaml

# Register the agent with endpoint
python -m agenthub_server.cli register-agent \
  --config my_http_agent.yaml \
  --deployment-type http \
  --endpoint-url http://localhost:8001
```

### 4. List Available Agents

```bash
python -m agenthub_server.cli list-agents
```

### 5. Hire Agents via API

```python
import httpx
import asyncio

async def hire_agent():
    client = httpx.AsyncClient()
    
    # Submit task
    response = await client.post("http://localhost:8080/tasks", json={
        "agent_id": "agent-123",
        "endpoint": "",  # Not needed for ACP agents
        "parameters": {
            "prompt": "What are the symptoms of vitamin D deficiency?"
        },
        "timeout": 30
    })
    
    if response.status_code == 200:
        task_info = response.json()
        task_id = task_info["task_id"]
        
        # Wait for completion
        while True:
            status_response = await client.get(f"http://localhost:8080/tasks/{task_id}")
            task_status = status_response.json()
            
            if task_status["status"] == "completed":
                print("Response:", task_status["result"]["response"])
                break
            elif task_status["status"] == "failed":
                print("Error:", task_status["error"])
                break
            
            await asyncio.sleep(2)
    
    await client.aclose()

# Run the example
asyncio.run(hire_agent())
```

## Agent Configuration Details

### CodeAgent Configuration

```yaml
agent_config:
  type: "code_agent"
  name: "my_code_agent"
  description: "Agent with code execution and tool access"
  model_id: "openai/gpt-4"
  tools: 
    - "DuckDuckGoSearchTool"
    - "VisitWebpageTool"
  system_prompt: "You are a helpful AI assistant with access to search and web browsing tools."
```

### LLMAgent Configuration

```yaml
agent_config:
  type: "llm_agent"
  name: "my_llm_agent"
  description: "Pure language model agent"
  model_id: "openai/gpt-4"
  system_prompt: "You are a creative writing assistant. Help users with storytelling and creative writing."
```

### ToolAgent Configuration

```yaml
agent_config:
  type: "tool_agent"
  name: "my_tool_agent"
  description: "Custom tool-based agent"
  tools: ["custom_tool_1", "custom_tool_2"]
```

## Environment Variables

```bash
# Required for OpenAI models
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Custom model configurations
export ANTHROPIC_API_KEY="your-anthropic-key"
export GROQ_API_KEY="your-groq-key"
```

## Dependencies

### Core Dependencies
```bash
pip install acp-sdk smolagents python-dotenv
```

### Optional Dependencies
```bash
# For specific tools
pip install duckduckgo-search beautifulsoup4

# For additional models
pip install anthropic groq
```

## Development

### Running the Demo

```bash
# Start the server
python -m agenthub_server.cli serve --port 8080 --no-auth

# In another terminal, run the demo
cd examples
python acp_demo.py
```

### Creating Custom Agents

1. **Define Agent Configuration**
   ```yaml
   agent_config:
     type: "code_agent"
     name: "custom_agent"
     description: "My custom agent"
     model_id: "openai/gpt-4"
     tools: ["DuckDuckGoSearchTool"]
     system_prompt: "Custom instructions for the agent"
   ```

2. **Register the Agent**
   ```bash
   python -m agenthub_server.cli register-agent \
     --config custom_agent.yaml \
     --deployment-type acp
   ```

3. **Test the Agent**
   ```python
   # Use the API to submit tasks to your agent
   ```

## API Endpoints

### Agent Registration
```http
POST /agents/register
Content-Type: application/json

{
  "metadata": {...},
  "agent_config": {...},
  "deployment_type": "acp"
}
```

### Task Submission
```http
POST /tasks
Content-Type: application/json

{
  "agent_id": "agent-123",
  "endpoint": "",
  "parameters": {
    "prompt": "Your task description"
  },
  "timeout": 30
}
```

### Task Status
```http
GET /tasks/{task_id}
```

## Migration from HTTP to ACP

### 1. Update Configuration
- Add `agent_config` section to your agent configuration
- Remove `endpoints` section (not needed for ACP)
- Change deployment type from `http` to `acp`

### 2. Re-register Agent
```bash
python -m agenthub_server.cli register-agent \
  --config updated_agent.yaml \
  --deployment-type acp
```

### 3. Update Task Submissions
- Remove `endpoint` parameter from task requests
- Use `prompt` parameter instead of endpoint-specific parameters
- All ACP agents use the same interface

## Monitoring and Debugging

### Server Logs
```bash
# Enable debug logging
python -m agenthub_server.cli serve --log-level debug
```

### Agent Lifecycle Monitoring
The server logs show:
- Agent server creation
- Task execution
- Agent cleanup
- Error handling

### Database Queries
```sql
-- View agent configurations
SELECT id, name, deployment_type, agent_config FROM agents;

-- View task history
SELECT task_id, agent_id, status, execution_time FROM tasks;
```

## Performance Considerations

### Resource Usage
- ACP agents use temporary processes (2-5 seconds startup time)
- Each agent server uses ~50-100MB RAM during execution
- Automatic cleanup prevents resource leaks

### Scaling
- Multiple tasks can run in parallel (different ports)
- Port pool management (9000-9999 by default)
- Configurable timeouts and limits

### Best Practices
1. Use appropriate timeout values (30-60 seconds)
2. Monitor active server count
3. Implement proper error handling
4. Consider caching for frequently used agents

## Troubleshooting

### Common Issues

1. **"acp_sdk not available"**
   ```bash
   pip install acp-sdk
   ```

2. **"No available ports"**
   - Check for stuck processes: `lsof -i :9000-9999`
   - Restart the hub server

3. **"Agent execution failed"**
   - Check OpenAI API key: `echo $OPENAI_API_KEY`
   - Verify agent configuration
   - Check server logs

4. **"Task timeout"**
   - Increase timeout value
   - Check model response time
   - Verify tool availability

### Debug Mode
```bash
python -m agenthub_server.cli serve --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.