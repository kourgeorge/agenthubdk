from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agenthub-sdk",
    version="0.1.0",
    author="AgentHub Team",
    author_email="support@agenthub.ai",
    description="Python SDK for AgentHub - AI Agent Hiring System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agenthub/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "langchain": [
            "langchain>=0.1.0",
            "langchain-openai>=0.1.0",
            "chromadb>=0.4.0",
        ],
        "crewai": [
            "crewai>=0.1.0",
        ],
        "full": [
            # Include all optional dependencies
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "langchain>=0.1.0",
            "langchain-openai>=0.1.0",
            "chromadb>=0.4.0",
            "crewai>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agenthub=agenthub.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agenthub": ["templates/*.yaml", "templates/*.json"],
    },
)