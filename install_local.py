#!/usr/bin/env python3
"""
Local Installation Verification Script for AgentHub SDK

This script helps verify that the AgentHub SDK was installed correctly
from local source code and shows what components are available.
"""

import sys
import subprocess
from typing import List, Tuple

def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def check_import(module_name: str, component_name: str = None) -> bool:
    """Check if a module/component can be imported"""
    try:
        if component_name:
            exec(f"from {module_name} import {component_name}")
        else:
            exec(f"import {module_name}")
        return True
    except ImportError:
        return False

def main():
    print("🔍 AgentHub SDK Local Installation Verification")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version compatible")
    
    print("\n📦 Core SDK Components:")
    
    # Test core imports
    core_tests = [
        ("agenthub.models", "AgentMetadata", "Agent models"),
        ("agenthub.models", "PricingModel", "Pricing models"),
        ("agenthub.decorators", "endpoint", "Endpoint decorator"),
        ("agenthub", "AgentMetadata", "Core exports"),
    ]
    
    core_available = True
    for module, component, description in core_tests:
        if check_import(module, component):
            print(f"   ✅ {description}: {module}.{component}")
        else:
            print(f"   ❌ {description}: {module}.{component}")
            core_available = False
    
    print("\n🚀 Advanced Components:")
    
    # Test advanced imports  
    advanced_tests = [
        ("agenthub.agent_builder", "AgentBuilder", "Agent Builder (requires FastAPI)"),
        ("agenthub.client", "AgentHubClient", "API Client (requires httpx)"),
        ("agenthub.server", "serve_agent", "HTTP Server (requires FastAPI)"),
        ("agenthub.cli", "main", "CLI Tools (requires typer)"),
    ]
    
    advanced_available = True
    for module, component, description in advanced_tests:
        if check_import(module, component):
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description}")
            advanced_available = False
    
    print("\n🔧 Optional Framework Integration:")
    
    # Test optional framework support
    framework_tests = [
        ("langchain", None, "LangChain support"),
        ("crewai", None, "CrewAI support"),
        ("pytest", None, "Testing framework"),
    ]
    
    for module, component, description in framework_tests:
        if check_import(module, component):
            print(f"   ✅ {description}")
        else:
            print(f"   ⚪ {description} (optional)")
    
    print("\n🧪 Functional Tests:")
    
    # Test basic functionality
    try:
        from agenthub import AgentMetadata, endpoint
        
        # Test model creation
        metadata = AgentMetadata(
            name="Test Agent",
            description="Test agent for verification",
            category="test"
        )
        print(f"   ✅ Model creation: Created agent '{metadata.name}'")
        
        # Test decorator
        @endpoint("/test")
        def test_endpoint(request):
            return {"status": "ok"}
        
        print("   ✅ Decorator usage: @endpoint decorator works")
        
        # Test endpoint execution
        result = test_endpoint({"test": "data"})
        if result.get("status") == "ok":
            print("   ✅ Endpoint execution: Test endpoint works")
        else:
            print("   ❌ Endpoint execution: Test endpoint failed")
            
    except Exception as e:
        print(f"   ❌ Functional test failed: {e}")
        core_available = False
    
    print("\n🎯 CLI Tools Test:")
    
    # Test CLI
    exit_code, stdout, stderr = run_command([sys.executable, "-m", "agenthub.cli", "--help"])
    if exit_code == 0:
        print("   ✅ CLI accessible via: python -m agenthub.cli")
    else:
        print("   ❌ CLI not accessible")
    
    # Test direct agenthub command
    exit_code, stdout, stderr = run_command(["agenthub", "--help"])
    if exit_code == 0:
        print("   ✅ CLI accessible via: agenthub")
    else:
        print("   ⚪ CLI command 'agenthub' not in PATH (may need to restart shell)")
    
    print("\n📊 Installation Summary:")
    
    if core_available:
        print("   ✅ Core SDK: Ready for zero-dependency development")
    else:
        print("   ❌ Core SDK: Installation issues detected")
    
    if advanced_available:
        print("   ✅ Advanced Features: HTTP servers, CLI tools, API client")
    else:
        print("   ⚪ Advanced Features: Some dependencies missing")
    
    print("\n🚀 Next Steps:")
    print("   1. Test basic functionality: python simple_local_demo.py")
    print("   2. Try examples: python examples/basic_agent.py")
    if advanced_available:
        print("   3. Use CLI: agenthub --help")
        print("   4. Start server: agenthub serve --config config.yaml")
    else:
        print("   3. Install full dependencies: pip install -e .[full]")
    
    return core_available

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)