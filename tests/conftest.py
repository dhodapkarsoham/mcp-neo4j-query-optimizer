#!/usr/bin/env python3
"""
Pytest configuration and fixtures
"""

import pytest
import os
from unittest.mock import Mock, patch


@pytest.fixture
def mock_neo4j_env():
    """Mock Neo4j environment variables"""
    with patch.dict('os.environ', {
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'password'
    }):
        yield


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver and session"""
    mock_driver = Mock()
    mock_session = Mock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.run.return_value.consume.return_value = None
    
    with patch('src.mcp_neo4j_optimizer.agent.GraphDatabase') as mock_graph_db:
        mock_graph_db.driver.return_value = mock_driver
        yield mock_driver, mock_session


@pytest.fixture
def sample_operators():
    """Sample query plan operators for testing"""
    return [
        {
            "operator": "AllNodesScan",
            "estimated_rows": 1000,
            "db_hits": 1000,
            "depth": 0
        },
        {
            "operator": "Filter",
            "estimated_rows": 100,
            "db_hits": 0,
            "depth": 1
        },
        {
            "operator": "Limit",
            "estimated_rows": 10,
            "db_hits": 0,
            "depth": 2
        }
    ]


@pytest.fixture
def sample_query_plan():
    """Sample query plan for testing"""
    return {
        "operator": "AllNodesScan",
        "estimated_rows": 1000,
        "db_hits": 1000,
        "depth": 0,
        "children": [
            {
                "operator": "Filter",
                "estimated_rows": 100,
                "db_hits": 0,
                "depth": 1,
                "children": []
            }
        ]
    }


@pytest.fixture
def sample_cypher_queries():
    """Sample Cypher queries for testing"""
    return {
        "simple_read": "MATCH (n) RETURN n",
        "labeled_read": "MATCH (n:Person) RETURN n",
        "filtered_read": "MATCH (n:Person) WHERE n.age > 25 RETURN n",
        "complex_read": "MATCH (n:Person)-[r:KNOWS]->(m:Person) WHERE n.age > 25 AND m.city = 'NYC' RETURN n, m",
        "write_query": "CREATE (n:Person {name: 'John', age: 30})",
        "update_query": "MATCH (n:Person) SET n.age = 31",
        "delete_query": "MATCH (n:Person) DELETE n"
    }
