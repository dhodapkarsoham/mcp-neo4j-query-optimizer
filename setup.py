#!/usr/bin/env python3
"""
Setup script for MCP Neo4j Query Optimizer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-neo4j-query-optimizer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP Server for Neo4j Query Optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mcp-neo4j-query-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "neo4j>=5.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-neo4j-query-optimizer=mcp_neo4j_optimizer.agent:main",
        ],
    },
    keywords="mcp neo4j query-optimization cypher",
    project_urls={
        "Bug Reports": "https://github.com/your-username/mcp-neo4j-query-optimizer/issues",
        "Source": "https://github.com/your-username/mcp-neo4j-query-optimizer",
        "Documentation": "https://github.com/your-username/mcp-neo4j-query-optimizer#readme",
    },
) 