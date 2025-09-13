#!/usr/bin/env python3
"""
Unit tests for MCP tools and agent functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.mcp_neo4j_optimizer.agent import (
    Neo4jOptimizerAgent,
    handle_request,
    handle_initialize,
    list_tools,
    call_tool,
    optimize_neo4j_query,
    analyze_query_plan_only,
    error_response
)


class TestMCPHandlers:
    """Test cases for MCP request handlers"""
    
    def test_handle_initialize(self):
        """Test MCP initialize handler"""
        params = {"protocolVersion": "2025-06-18"}
        request_id = 1
        
        response = handle_initialize(params, request_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2025-06-18"
        assert response["result"]["serverInfo"]["name"] == "neo4j-optimizer-agent"
        assert response["result"]["serverInfo"]["version"] == "2.0.0"
    
    def test_list_tools(self):
        """Test tools list handler"""
        request_id = 1
        
        response = list_tools(request_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "tools" in response["result"]
        
        tools = response["result"]["tools"]
        assert len(tools) == 2
        
        # Check optimize-neo4j-query tool
        optimize_tool = next(t for t in tools if t["name"] == "optimize-neo4j-query")
        assert optimize_tool["description"] is not None
        assert "inputSchema" in optimize_tool
        assert "query" in optimize_tool["inputSchema"]["properties"]
        assert "database" in optimize_tool["inputSchema"]["properties"]
        assert optimize_tool["inputSchema"]["required"] == ["query"]
        
        # Check analyze-query-plan tool
        analyze_tool = next(t for t in tools if t["name"] == "analyze-query-plan")
        assert analyze_tool["description"] is not None
        assert "inputSchema" in analyze_tool
        assert "query" in analyze_tool["inputSchema"]["properties"]
        assert "database" in analyze_tool["inputSchema"]["properties"]
        assert analyze_tool["inputSchema"]["required"] == ["query"]
    
    def test_error_response(self):
        """Test error response creation"""
        request_id = 1
        error_message = "Test error"
        
        response = error_response(request_id, error_message)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert response["error"]["message"] == error_message
    
    def test_handle_request_initialize(self):
        """Test handle_request with initialize method"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"}
        }
        
        response = handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
    
    def test_handle_request_tools_list(self):
        """Test handle_request with tools/list method"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "tools" in response["result"]
    
    def test_handle_request_unknown_method(self):
        """Test handle_request with unknown method"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "unknown_method"
        }
        
        response = handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert "Unknown method: unknown_method" in response["error"]["message"]


class TestMCPTools:
    """Test cases for MCP tool functions"""
    
    @patch('src.mcp_neo4j_optimizer.agent.Neo4jOptimizerAgent')
    def test_optimize_neo4j_query_success(self, mock_agent_class):
        """Test successful query optimization"""
        # Mock the agent and its methods
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Mock query plan data
        mock_plan_data = {
            "explain_plan": {"operator": "AllNodesScan", "children": []},
            "profile_plan": None,
            "execution_time": 100,
            "query": "MATCH (n) RETURN n"
        }
        
        # Mock performance issues
        from src.mcp_neo4j_optimizer.agent import PerformanceIssue, Severity
        mock_issues = [
            PerformanceIssue(
                severity=Severity.CRITICAL,
                operator="AllNodesScan",
                issue="Full database scan",
                suggestion="Add labels",
                impact="Very slow",
                depth=0
            )
        ]
        
        # Mock optimized query
        mock_optimized_query = "MATCH (n:Node) RETURN n LIMIT 1000"
        
        # Mock optimized plan data
        mock_optimized_plan_data = {
            "explain_plan": {"operator": "NodeByLabelScan", "children": []},
            "profile_plan": None,
            "execution_time": 50,
            "query": mock_optimized_query
        }
        
        # Mock comparison
        mock_comparison = {
            "original_operators": {"AllNodesScan": 1},
            "optimized_operators": {"NodeByLabelScan": 1},
            "original_estimated_rows": 1000,
            "optimized_estimated_rows": 100,
            "improvements": ["✅ Reduced full database scans"]
        }
        
        # Mock analysis
        mock_analysis = {
            "query": "MATCH (n) RETURN n",
            "query_type": "read",
            "complexity": "simple",
            "query_patterns": ["node matching"],
            "operators": [{"operator": "AllNodesScan", "estimated_rows": 1000, "db_hits": 100}],
            "summary": {"total_operators": 1, "leaf_operators": 1, "updating_operators": 0, "eager_operators": 0, "estimated_total_rows": 1000, "estimated_db_hits": 100},
            "performance_indicators": ["full_scan"],
            "query_metadata": {"has_where_clause": False, "has_limit": False},
            "performance_characteristics": "Full database scan detected"
        }
        
        # Set up mock return values
        mock_agent.get_query_plan.side_effect = [mock_plan_data, mock_optimized_plan_data]
        mock_agent.analyze_plan_issues.return_value = [{"operator": "AllNodesScan", "estimated_rows": 1000, "db_hits": 100}]
        mock_agent.generate_optimized_query.return_value = mock_optimized_query
        mock_agent.compare_plans.return_value = mock_comparison
        mock_agent.analyzer.analyze_query.return_value = mock_analysis
        mock_agent._extract_operators_from_plan.return_value = [{"operator": "AllNodesScan", "estimated_rows": 1000, "db_hits": 100, "depth": 0}]
        
        # Test the function
        arguments = {"query": "MATCH (n) RETURN n"}
        result = optimize_neo4j_query(arguments)
        
        # Verify the result contains expected content
        assert "Neo4j Query Optimization Analysis" in result
        assert "MATCH (n) RETURN n" in result
        assert "MATCH (n:Node) RETURN n LIMIT 1000" in result
        assert "✅ Reduced full database scans" in result
    
    def test_optimize_neo4j_query_missing_query(self):
        """Test optimize_neo4j_query with missing query parameter"""
        arguments = {}
        
        with pytest.raises(ValueError, match="Query is required"):
            optimize_neo4j_query(arguments)
    
    @patch('src.mcp_neo4j_optimizer.agent.Neo4jOptimizerAgent')
    def test_analyze_query_plan_only_success(self, mock_agent_class):
        """Test successful query plan analysis"""
        # Mock the agent and its methods
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Mock query plan data
        mock_plan_data = {
            "explain_plan": {"operator": "AllNodesScan", "children": []},
            "profile_plan": None,
            "execution_time": 100,
            "query": "MATCH (n) RETURN n"
        }
        
        # Mock performance issues
        from src.mcp_neo4j_optimizer.agent import PerformanceIssue, Severity
        mock_issues = [
            PerformanceIssue(
                severity=Severity.CRITICAL,
                operator="AllNodesScan",
                issue="Full database scan",
                suggestion="Add labels",
                impact="Very slow",
                depth=0
            )
        ]
        
        # Mock analysis
        mock_analysis = {
            "query": "MATCH (n) RETURN n",
            "query_type": "read",
            "complexity": "simple",
            "query_patterns": ["node matching"],
            "operators": [{"operator": "AllNodesScan", "estimated_rows": 1000, "db_hits": 100}],
            "summary": {"total_operators": 1, "leaf_operators": 1, "updating_operators": 0, "eager_operators": 0, "estimated_total_rows": 1000, "estimated_db_hits": 100},
            "performance_indicators": ["full_scan"],
            "query_metadata": {"has_where_clause": False, "has_limit": False},
            "performance_characteristics": "Full database scan detected"
        }
        
        # Set up mock return values
        mock_agent.get_query_plan.return_value = mock_plan_data
        mock_agent.analyze_plan_issues.return_value = [{"operator": "AllNodesScan", "estimated_rows": 1000, "db_hits": 100}]
        mock_agent.analyzer.analyze_query.return_value = mock_analysis
        mock_agent._extract_operators_from_plan.return_value = [{"operator": "AllNodesScan", "estimated_rows": 1000, "db_hits": 100, "depth": 0}]
        
        # Mock the conversational interface
        mock_agent.conversational_interface.generate_rich_context.return_value = "Neo4j Query Analysis Context\n\n## Query Overview\n- **Type**: read query\n- **Complexity**: simple"
        
        # Test the function
        arguments = {"query": "MATCH (n) RETURN n"}
        result = analyze_query_plan_only(arguments)
        
        # Verify the result contains expected content
        assert "Query Plan Analysis" in result
        assert "MATCH (n) RETURN n" in result
        assert "Neo4j Query Analysis Context" in result
    
    def test_analyze_query_plan_only_missing_query(self):
        """Test analyze_query_plan_only with missing query parameter"""
        arguments = {}
        
        with pytest.raises(ValueError, match="Query is required"):
            analyze_query_plan_only(arguments)
    
    def test_call_tool_optimize_query(self):
        """Test call_tool with optimize-neo4j-query"""
        with patch('src.mcp_neo4j_optimizer.agent.optimize_neo4j_query') as mock_optimize:
            mock_optimize.return_value = "Test optimization result"
            
            params = {
                "name": "optimize-neo4j-query",
                "arguments": {"query": "MATCH (n) RETURN n"}
            }
            request_id = 1
            
            response = call_tool(params, request_id)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert response["result"]["content"][0]["text"] == "Test optimization result"
            mock_optimize.assert_called_once_with({"query": "MATCH (n) RETURN n"})
    
    def test_call_tool_analyze_plan(self):
        """Test call_tool with analyze-query-plan"""
        with patch('src.mcp_neo4j_optimizer.agent.analyze_query_plan_only') as mock_analyze:
            mock_analyze.return_value = "Test analysis result"
            
            params = {
                "name": "analyze-query-plan",
                "arguments": {"query": "MATCH (n) RETURN n"}
            }
            request_id = 1
            
            response = call_tool(params, request_id)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert response["result"]["content"][0]["text"] == "Test analysis result"
            mock_analyze.assert_called_once_with({"query": "MATCH (n) RETURN n"})
    
    def test_call_tool_unknown_tool(self):
        """Test call_tool with unknown tool name"""
        params = {
            "name": "unknown-tool",
            "arguments": {}
        }
        request_id = 1
        
        response = call_tool(params, request_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert "Unknown tool: unknown-tool" in response["error"]["message"]


class TestNeo4jOptimizerAgent:
    """Test cases for Neo4jOptimizerAgent class"""
    
    @patch('src.mcp_neo4j_optimizer.agent.GraphDatabase')
    def test_agent_initialization_with_connection(self, mock_graph_db):
        """Test agent initialization with successful Neo4j connection"""
        # Mock the driver and session
        mock_driver = Mock()
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_context_manager
        mock_session.run.return_value.consume.return_value = None
        mock_graph_db.driver.return_value = mock_driver
        
        # Mock environment variables
        with patch.dict('os.environ', {
            'NEO4J_URI': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'password'
        }):
            agent = Neo4jOptimizerAgent()
            
            assert agent is not None
            assert hasattr(agent, 'analyzer')
            assert hasattr(agent, 'conversational_interface')
            mock_graph_db.driver.assert_called_once()
    
    @patch('src.mcp_neo4j_optimizer.agent.GraphDatabase')
    def test_agent_initialization_without_connection(self, mock_graph_db):
        """Test agent initialization without Neo4j connection"""
        # Mock environment variables to be empty
        with patch.dict('os.environ', {}, clear=True):
            # The agent should still initialize but with a warning
            agent = Neo4jOptimizerAgent()
            assert agent is not None
            assert hasattr(agent, 'analyzer')
            assert hasattr(agent, 'conversational_interface')
    
    def test_plan_to_dict_with_plan_object(self):
        """Test _plan_to_dict with Neo4j plan object"""
        # Create a mock plan object
        mock_plan = Mock()
        mock_plan.operator_type = "AllNodesScan"
        mock_plan.arguments = {"EstimatedRows": 1000}
        mock_plan.identifiers = ["n"]
        mock_plan.children = []
        
        agent = Neo4jOptimizerAgent()
        result = agent._plan_to_dict(mock_plan)
        
        assert result["operator"] == "AllNodesScan"
        assert result["estimated_rows"] == 1000
        assert result["identifiers"] == ["n"]
        assert result["children"] == []
    
    def test_plan_to_dict_with_dict(self):
        """Test _plan_to_dict with dictionary input"""
        plan_dict = {
            "operator": "AllNodesScan",
            "estimated_rows": 1000,
            "children": []
        }
        
        agent = Neo4jOptimizerAgent()
        result = agent._plan_to_dict(plan_dict)
        
        assert result == plan_dict
    
    def test_plan_to_dict_with_none(self):
        """Test _plan_to_dict with None input"""
        agent = Neo4jOptimizerAgent()
        result = agent._plan_to_dict(None)
        
        assert result == {}
    
    def test_extract_operators_from_plan(self):
        """Test _extract_operators_from_plan"""
        plan = {
            "operator": "AllNodesScan",
            "estimated_rows": 1000,
            "db_hits": 100,
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
        
        agent = Neo4jOptimizerAgent()
        operators = agent._extract_operators_from_plan(plan)
        
        assert len(operators) == 2
        assert operators[0]["operator"] == "AllNodesScan"
        assert operators[0]["depth"] == 0
        assert operators[1]["operator"] == "Filter"
        assert operators[1]["depth"] == 1
    
    def test_compare_plans(self):
        """Test compare_plans method"""
        original_plan = {
            "operator": "AllNodesScan",
            "estimated_rows": 1000,
            "children": []
        }
        
        optimized_plan = {
            "operator": "NodeByLabelScan",
            "estimated_rows": 100,
            "children": []
        }
        
        agent = Neo4jOptimizerAgent()
        comparison = agent.compare_plans(original_plan, optimized_plan)
        
        assert "original_operators" in comparison
        assert "optimized_operators" in comparison
        assert "original_estimated_rows" in comparison
        assert "optimized_estimated_rows" in comparison
        assert "improvements" in comparison
        
        assert comparison["original_estimated_rows"] == 1000
        assert comparison["optimized_estimated_rows"] == 100
        assert len(comparison["improvements"]) > 0
    
    def test_identify_improvements(self):
        """Test _identify_improvements method"""
        original_ops = {"AllNodesScan": 1, "CartesianProduct": 1}
        optimized_ops = {"NodeByLabelScan": 1, "Limit": 1}
        
        agent = Neo4jOptimizerAgent()
        improvements = agent._identify_improvements(original_ops, optimized_ops)
        
        assert "✅ Reduced full database scans" in improvements
        assert "✅ Eliminated cartesian products" in improvements
        assert "✅ Added efficient label-based scans" in improvements
        assert "✅ Added result limiting" in improvements


if __name__ == "__main__":
    pytest.main([__file__])
