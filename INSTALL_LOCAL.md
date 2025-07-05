# 🔧 Installing AgentHub SDK from Local Source Code

This guide shows you how to install the AgentHub Python SDK from the local source code repository instead of from PyPI.

## 🚀 Quick Start

### 1. **Navigate to Repository**
```bash
cd /path/to/agenthubdk
# Windows: cd C:\repositories\agenthubdk
```

### 2. **Choose Installation Type**

#### **Full Installation (Recommended)**
Installs everything including CLI tools, framework integrations, and development tools:
```bash
pip install -e .[full]
```

#### **Basic Installation**
Installs core SDK with HTTP server capabilities:
```bash
pip install -e .
```

#### **Zero Dependencies**
Just run the demos directly without installing:
```bash
python simple_local_demo.py
```

### 3. **Verify Installation**
```bash
python install_local.py
```

## 📦 Installation Options Explained

### **Option 1: Editable Install (Development Mode) - Recommended**

```bash
# Core functionality only
pip install -e .

# With specific features
pip install -e .[langchain]     # LangChain integration
pip install -e .[crewai]        # CrewAI integration  
pip install -e .[dev]           # Development tools

# Everything included
pip install -e .[full]          # All features + dev tools
```

**Benefits of `-e` (editable install):**
- ✅ Changes to source code are immediately reflected
- ✅ Perfect for development and testing
- ✅ No need to reinstall after code changes
- ✅ Can easily switch between branches

### **Option 2: Regular Install**

```bash
# Core functionality only
pip install .

# Full installation
pip install .[full]
```

**When to use regular install:**
- ✅ Production deployments
- ✅ When you don't plan to modify the code
- ✅ Slightly faster import times

### **Option 3: Direct Usage (No Installation)**

```bash
# Run demos directly
python simple_local_demo.py
python local_http_agent.py

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/agenthubdk"
python -c "from agenthub import AgentMetadata; print('Works!')"
```

## 🎯 Installation Levels

### **Level 1: Zero Dependencies**
```bash
# No installation needed - just run:
python simple_local_demo.py
```
**What you get:**
- ✅ Core models (`AgentMetadata`, `PricingModel`)
- ✅ Decorators (`@endpoint`, `@capability`)
- ✅ Local agent development
- ✅ Works with Python standard library only

### **Level 2: Basic SDK**
```bash
pip install -e .
```
**What you get:**
- ✅ Everything from Level 1
- ✅ `AgentBuilder` for HTTP servers
- ✅ FastAPI integration
- ✅ Auto-reload development server
- ✅ Basic CLI functionality

### **Level 3: Full SDK**
```bash
pip install -e .[full]
```
**What you get:**
- ✅ Everything from Level 2
- ✅ Complete CLI tools (`agenthub` command)
- ✅ AgentHub API client
- ✅ LangChain integration
- ✅ CrewAI integration
- ✅ Development tools (pytest, black, mypy)

## 🔍 Verification & Testing

### **Run Installation Verification**
```bash
python install_local.py
```

### **Test Core Functionality**
```bash
# Test zero-dependency demo
python simple_local_demo.py

# Test HTTP server demo  
python local_http_agent.py

# Test with examples
python examples/basic_agent.py
```

### **Test CLI Tools** (Full installation only)
```bash
# Check CLI is available
agenthub --help

# Alternative access
python -m agenthub.cli --help

# Test CLI commands
agenthub init --name test-agent
agenthub validate --config agent_config.yaml
```

### **Test Framework Integration** (With extras)
```bash
# Test LangChain example (requires [langchain])
python examples/rag_agent.py

# Test CrewAI example (requires [crewai])
python examples/crewai_agent.py
```

## 🛠️ Development Setup

### **For SDK Development**
```bash
# Clone and setup
git clone https://github.com/kourgeorge/agenthubdk
cd agenthubdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode with all tools
pip install -e .[full]

# Verify everything works
python install_local.py
```

### **For Agent Development**
```bash
# Install just what you need for building agents
pip install -e .

# Or start with zero dependencies
python simple_local_demo.py
```

## 📋 Available Extras

| Extra | Description | Includes |
|-------|-------------|----------|
| `[full]` | Everything | All features + dev tools |
| `[dev]` | Development tools | pytest, black, flake8, mypy |
| `[langchain]` | LangChain integration | langchain, langchain-openai, chromadb |
| `[crewai]` | CrewAI integration | crewai |

### **Combining Extras**
```bash
# Multiple extras
pip install -e .[langchain,dev]

# All extras individually
pip install -e .[dev,langchain,crewai]

# Same as [full]
pip install -e .[full]
```

## 🚨 Troubleshooting

### **ImportError: No module named 'agenthub'**
```bash
# Make sure you're in the right directory
cd /path/to/agenthubdk

# Install in editable mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### **Command 'agenthub' not found**
```bash
# Install with full extras
pip install -e .[full]

# Or use module access
python -m agenthub.cli --help

# Check if it's in PATH
which agenthub
```

### **FastAPI/Pydantic Errors**
```bash
# Install base dependencies
pip install -e .

# Or check what's missing
python install_local.py
```

### **Framework Integration Issues**
```bash
# Install specific extras
pip install -e .[langchain]  # For LangChain
pip install -e .[crewai]     # For CrewAI

# Or install everything
pip install -e .[full]
```

## 🎯 Common Use Cases

### **Just Testing the SDK**
```bash
# No installation needed
python simple_local_demo.py
python install_local.py
```

### **Building Agents**
```bash
# Basic installation
pip install -e .

# Test with examples
python examples/basic_agent.py
```

### **Full Development**
```bash
# Everything included
pip install -e .[full]

# Verify all features work
python install_local.py
agenthub --help
```

### **Framework-Specific Development**
```bash
# For LangChain developers
pip install -e .[langchain]
python examples/rag_agent.py

# For CrewAI developers  
pip install -e .[crewai]
python examples/crewai_agent.py
```

## 📊 Installation Success Indicators

### **Core SDK Working**
```
✅ python simple_local_demo.py runs without errors
✅ from agenthub import AgentMetadata works
✅ @endpoint decorator functions properly
```

### **Full SDK Working**
```
✅ agenthub --help shows CLI options
✅ python examples/basic_agent.py runs HTTP server
✅ All import tests pass in install_local.py
```

### **Framework Integration Working**
```
✅ python examples/rag_agent.py (LangChain)
✅ python examples/crewai_agent.py (CrewAI)
✅ No import errors for optional frameworks
```

## 🔄 Updating Local Installation

### **Pull Latest Changes**
```bash
git pull origin main

# No reinstall needed with editable install (-e)
# Changes are immediately available
```

### **Update Dependencies**
```bash
# Reinstall to get new dependencies
pip install -e .[full]

# Or update specific packages
pip install --upgrade fastapi pydantic
```

### **Switch Branches**
```bash
git checkout feature-branch

# Editable install automatically uses new code
# No reinstall needed
```

---

## 🎉 You're Ready!

Once installed, you can:

1. **Start building agents**: `python examples/basic_agent.py`
2. **Use CLI tools**: `agenthub init --name my-agent`
3. **Test locally**: `python simple_local_demo.py`
4. **Integrate frameworks**: Use LangChain, CrewAI examples
5. **Deploy to production**: When ready, publish to AgentHub marketplace

For more examples and documentation, see:
- `README.md` - Complete SDK documentation
- `examples/` - Working examples for different frameworks
- `simple_local_demo.py` - Zero-dependency demonstration