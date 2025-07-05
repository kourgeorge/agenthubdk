"""
CrewAI Research Team Example

This example demonstrates how to create an agent using CrewAI framework
with the AgentHub SDK integration.
"""

import os
from agenthub import AgentBuilder, publish_agent

# Optional: CrewAI imports (install with: pip install crewai)
try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("CrewAI not available. Install with: pip install agenthub-sdk[crewai]")

def create_research_crew():
    """Create a research crew using CrewAI"""
    
    if not CREWAI_AVAILABLE:
        print("CrewAI not available - using fallback implementation")
        return None
    
    # Define Agents
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover cutting-edge developments in AI and data science',
        backstory='You work at a leading tech think tank. Your expertise lies in identifying emerging trends.',
        verbose=True,
        allow_delegation=False
    )

    writer = Agent(
        role='Tech Content Strategist',
        goal='Craft compelling content on tech advancements',
        backstory='You are a renowned Content Strategist, known for insightful and engaging articles.',
        verbose=True,
        allow_delegation=True
    )

    # Define Tasks
    research_task = Task(
        description='Conduct a comprehensive analysis of the latest advancements in AI in 2024.',
        expected_output='A comprehensive 3 paragraphs long report on the latest AI advancements.',
        agent=researcher
    )

    write_task = Task(
        description='Using the research analyst insights, develop an engaging blog post.',
        expected_output='A 4 paragraph blog post formatted as markdown.',
        agent=writer
    )

    # Create Crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=2
    )
    
    return crew, research_task, write_task

def create_crewai_agent():
    """Create a CrewAI agent using AgentHub"""
    
    # Create agent builder
    agent = AgentBuilder("ai-research-crew")
    
    # Initialize CrewAI system
    if CREWAI_AVAILABLE:
        crew, research_task, write_task = create_research_crew()
    else:
        crew = None
        research_task = None
        write_task = None
    
    @agent.endpoint("/research", description="Conduct research and write content")
    def run_research(request):
        """Run research crew on a topic"""
        topic = request.json.get("topic", "AI advancements")
        
        if crew and research_task and write_task:
            try:
                # Update task descriptions with custom topic
                research_task.description = f'Conduct comprehensive analysis of {topic}'
                write_task.description = f'Create engaging blog post about {topic}'
                
                result = crew.kickoff()
                return {
                    "content": str(result),
                    "topic": topic,
                    "status": "completed"
                }
            except Exception as e:
                return {"error": f"Research failed: {str(e)}"}
        else:
            # Fallback response
            return {
                "content": f"# Research Report: {topic}\n\nThis is a fallback response. CrewAI would normally conduct research and write content about {topic}.",
                "topic": topic,
                "status": "fallback",
                "note": "CrewAI not available - this is a simulated response"
            }
    
    @agent.endpoint("/analyze", description="Analyze a specific topic")
    def analyze_topic(request):
        """Analyze a specific topic using research agent"""
        topic = request.json.get("topic", "")
        depth = request.json.get("depth", "medium")
        
        if not topic:
            return {"error": "Topic is required"}
        
        # Simulated analysis (would use CrewAI researcher in real implementation)
        return {
            "analysis": f"Analysis of {topic} (depth: {depth})",
            "key_points": [
                f"Key finding 1 about {topic}",
                f"Key finding 2 about {topic}",
                f"Key finding 3 about {topic}"
            ],
            "conclusion": f"Conclusion about {topic}",
            "confidence": 0.85
        }
    
    @agent.endpoint("/write", description="Write content about a topic")
    def write_content(request):
        """Write content using content strategist agent"""
        topic = request.json.get("topic", "")
        style = request.json.get("style", "blog")
        length = request.json.get("length", "medium")
        
        if not topic:
            return {"error": "Topic is required"}
        
        # Simulated writing (would use CrewAI writer in real implementation)
        content = f"""# {topic}

## Introduction
This is an introduction to {topic}.

## Main Content
Here's the main content about {topic}, written in {style} style with {length} length.

## Conclusion
In conclusion, {topic} is an important subject worth exploring further.
"""
        
        return {
            "content": content,
            "topic": topic,
            "style": style,
            "length": length,
            "word_count": len(content.split())
        }
    
    @agent.endpoint("/crew-status", method="GET", description="Get crew status")
    def get_crew_status(request):
        """Get status of the research crew"""
        return {
            "crew_available": CREWAI_AVAILABLE,
            "agents": ["Senior Research Analyst", "Tech Content Strategist"] if CREWAI_AVAILABLE else [],
            "tasks": ["Research", "Writing"] if CREWAI_AVAILABLE else [],
            "status": "active" if CREWAI_AVAILABLE else "fallback"
        }
    
    # Set agent metadata
    agent.set_metadata({
        "name": "AI Research Crew",
        "description": "AI-powered research and content creation crew",
        "version": "1.0.0",
        "category": "research",
        "tags": ["research", "writing", "content", "ai", "crewai"],
        "pricing": {
            "type": "per_request",
            "price": 0.10
        },
        "author": "AgentHub Team",
        "license": "MIT"
    })
    
    return agent

if __name__ == "__main__":
    # Create the agent
    agent = create_crewai_agent()
    
    # Option 1: Serve locally for development
    from agenthub.server import serve_agent
    print("Starting CrewAI Research Agent server...")
    print("Available endpoints:")
    for endpoint in agent.get_endpoints():
        print(f"  - {endpoint}: {agent.get_endpoints()[endpoint]['description']}")
    
    serve_agent(agent, host="localhost", port=8000, reload=True)
    
    # Option 2: Publish to AgentHub (uncomment to use)
    # publish_agent(agent, api_key=os.getenv("AGENTHUB_API_KEY"))