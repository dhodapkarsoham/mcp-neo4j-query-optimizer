"""
MCP Neo4j Query Optimizer

A comprehensive MCP (Model Context Protocol) server for analyzing and optimizing Neo4j Cypher queries.
"""

__version__ = "0.1.0"
__author__ = "Neo4j Query Optimizer Team"

from .agent import Neo4jOptimizerAgent, main

__all__ = ["Neo4jOptimizerAgent", "main"]
