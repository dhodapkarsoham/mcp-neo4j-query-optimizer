#!/usr/bin/env python3
"""
Unit tests for Neo4jAnalyzer class
"""

import pytest
from src.mcp_neo4j_optimizer.agent import (
    Neo4jAnalyzer, 
    Severity, 
    PerformanceIssue, 
    QueryAnalysis,
    ConversationalInterface
)


class TestNeo4jAnalyzer:
    """Test cases for Neo4jAnalyzer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = Neo4jAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'analyze_operators')
    
    def test_classify_query_type(self):
        """Test query type classification"""
        # Read queries
        assert self.analyzer._classify_query_type("MATCH (n) RETURN n") == "read"
        assert self.analyzer._classify_query_type("MATCH (n:Person) WHERE n.age > 25 RETURN n") == "read"
        
        # Write queries
        assert self.analyzer._classify_query_type("CREATE (n:Person {name: 'John'})") == "write"
        
        # Update queries
        assert self.analyzer._classify_query_type("MATCH (n:Person) SET n.age = 30") == "update"
        assert self.analyzer._classify_query_type("MERGE (n:Person {name: 'John'})") == "update"
        
        # Delete queries
        assert self.analyzer._classify_query_type("MATCH (n:Person) DELETE n") == "delete"
        assert self.analyzer._classify_query_type("MATCH (n:Person) REMOVE n.age") == "delete"
        
        # Unknown queries
        assert self.analyzer._classify_query_type("SHOW DATABASES") == "unknown"
    
    def test_assess_query_complexity(self):
        """Test query complexity assessment"""
        # Simple queries
        assert self.analyzer._assess_query_complexity("MATCH (n) RETURN n") == "simple"
        assert self.analyzer._assess_query_complexity("MATCH (n) WHERE n.name = 'John' RETURN n") == "simple"
        
        # Medium complexity
        assert self.analyzer._assess_query_complexity("MATCH (n) WHERE n.age > 25 ORDER BY n.name LIMIT 10 RETURN n") == "medium"
        
        # Complex queries
        complex_query = "MATCH (n:Person)-[r:KNOWS]->(m:Person) WHERE n.age > 25 AND m.city = 'NYC' WITH n, COUNT(m) as friends MATCH (n)-[:WORKS_AT]->(c:Company) WHERE c.size > 1000 RETURN n.name, friends, c.name ORDER BY friends DESC LIMIT 5"
        assert self.analyzer._assess_query_complexity(complex_query) == "complex"
    
    def test_identify_query_patterns(self):
        """Test query pattern identification"""
        query = "MATCH (n:Person)-[r:KNOWS]->(m:Person) WHERE n.age > 25 ORDER BY n.name LIMIT 10 RETURN n, COUNT(m)"
        patterns = self.analyzer._identify_query_patterns(query)
        
        # The query has labeled nodes, so "node matching" should be detected
        assert "node matching" in patterns
        assert "relationship traversal" in patterns
        assert "property filtering" in patterns
        assert "result sorting" in patterns
        assert "result limiting" in patterns
        assert "aggregation" in patterns
    
    def test_analyze_performance_characteristics(self):
        """Test performance characteristics analysis"""
        # Query with full scan
        query1 = "MATCH (n) RETURN n"
        characteristics1 = self.analyzer._analyze_performance_characteristics(query1)
        assert "Full database scan" in characteristics1
        
        # Query without filtering
        query2 = "MATCH (n:Person) RETURN n"
        characteristics2 = self.analyzer._analyze_performance_characteristics(query2)
        assert "No filtering" in characteristics2
        
        # Well-structured query
        query3 = "MATCH (n:Person) WHERE n.age > 25 RETURN n LIMIT 10"
        characteristics3 = self.analyzer._analyze_performance_characteristics(query3)
        assert characteristics3 == "Query appears well-structured"
    
    def test_analyze_operators(self):
        """Test operator analysis"""
        operators = [
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
            }
        ]
        
        operator_data = self.analyzer.analyze_operators(operators, "MATCH (n) RETURN n")
        
        assert len(operator_data) == 2
        assert operator_data[0]["operator"] == "AllNodesScan"
        assert operator_data[0]["is_leaf"] == True
        assert operator_data[1]["operator"] == "Filter"
        assert operator_data[1]["is_leaf"] == False
    
    def test_analyze_query_metadata(self):
        """Test query metadata analysis"""
        query = "MATCH (n:Person) WHERE n.age > 25 ORDER BY n.name RETURN n LIMIT 10"
        analysis = self.analyzer.analyze_query(query, [])
        
        assert analysis["query_metadata"]["has_where_clause"] == True
        assert analysis["query_metadata"]["has_order_by"] == True
        assert analysis["query_metadata"]["has_limit"] == True
        assert analysis["query_metadata"]["has_aggregation"] == False
        assert analysis["query_metadata"]["has_relationships"] == False
    
    def test_analyze_query_comprehensive(self):
        """Test comprehensive query analysis"""
        operators = [
            {
                "operator": "AllNodesScan",
                "estimated_rows": 1000,
                "db_hits": 1000,
                "depth": 0
            }
        ]
        
        analysis = self.analyzer.analyze_query("MATCH (n) RETURN n", operators)
        
        assert isinstance(analysis, dict)
        assert analysis["query_type"] == "read"
        assert analysis["complexity"] == "simple"
        assert len(analysis["operators"]) > 0
        assert len(analysis["query_patterns"]) > 0
        assert analysis["summary"]["estimated_total_rows"] == 1000
        assert analysis["summary"]["estimated_db_hits"] == 1000
    
    def test_performance_indicators(self):
        """Test performance indicator extraction"""
        operators = [
            {
                "operator": "AllNodesScan",
                "estimated_rows": 150000,
                "db_hits": 150000,
                "depth": 0
            }
        ]
        
        analysis = self.analyzer.analyze_query("MATCH (n) RETURN n", operators)
        
        assert "high_row_count" in analysis["performance_indicators"]
        assert "full_scan" in analysis["performance_indicators"]


class TestConversationalInterface:
    """Test cases for ConversationalInterface class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = Neo4jAnalyzer()
        self.interface = ConversationalInterface(self.analyzer)
    
    def test_interface_initialization(self):
        """Test that interface initializes correctly"""
        assert self.interface is not None
        assert self.interface.analyzer == self.analyzer
    
    def test_generate_rich_context(self):
        """Test rich context generation"""
        analysis = {
            "query": "MATCH (n:Person) WHERE n.age > 25 RETURN n",
            "query_type": "read",
            "complexity": "medium",
            "query_patterns": ["node matching", "property filtering"],
            "operators": [
                {
                    "operator": "NodeByLabelScan",
                    "clean_operator": "NodeByLabelScan",
                    "estimated_rows": 1000,
                    "db_hits": 100,
                    "depth": 0,
                    "is_leaf": True,
                    "is_updating": False,
                    "is_eager": False,
                    "performance_characteristics": {
                        "operator_type": "NodeByLabelScan",
                        "estimated_rows": 1000,
                        "db_hits": 100,
                        "performance_indicators": ["high_row_count"]
                    }
                }
            ],
            "summary": {
                "total_operators": 1,
                "leaf_operators": 1,
                "updating_operators": 0,
                "eager_operators": 0,
                "estimated_total_rows": 1000,
                "estimated_db_hits": 100
            },
            "performance_indicators": ["high_row_count"],
            "query_metadata": {
                "has_where_clause": True,
                "has_order_by": False,
                "has_limit": False,
                "has_aggregation": False,
                "has_relationships": False
            },
            "performance_characteristics": "Some performance issues detected"
        }
        
        context = self.interface.generate_rich_context("MATCH (n:Person) WHERE n.age > 25 RETURN n", analysis)
        
        assert "Neo4j Query Analysis - Structured Data for MCP Client" in context
        assert "read query" in context
        assert "medium" in context
        assert "node matching" in context
        assert "NodeByLabelScan" in context
        assert "high_row_count" in context


class TestSeverityEnum:
    """Test cases for Severity enum"""
    
    def test_severity_values(self):
        """Test that severity enum has correct values"""
        assert Severity.CRITICAL.value == "Critical"
        assert Severity.HIGH.value == "High"
        assert Severity.MEDIUM.value == "Medium"
        assert Severity.LOW.value == "Low"
        assert Severity.INFO.value == "Info"


class TestPerformanceIssue:
    """Test cases for PerformanceIssue dataclass"""
    
    def test_performance_issue_creation(self):
        """Test PerformanceIssue creation"""
        issue = PerformanceIssue(
            severity=Severity.CRITICAL,
            operator="AllNodesScan",
            issue="Full database scan",
            suggestion="Add labels",
            impact="Very slow",
            depth=0,
            estimated_rows=1000,
            db_hits=1000
        )
        
        assert issue.severity == Severity.CRITICAL
        assert issue.operator == "AllNodesScan"
        assert issue.issue == "Full database scan"
        assert issue.suggestion == "Add labels"
        assert issue.impact == "Very slow"
        assert issue.depth == 0
        assert issue.estimated_rows == 1000
        assert issue.db_hits == 1000


class TestQueryAnalysis:
    """Test cases for QueryAnalysis dataclass"""
    
    def test_query_analysis_creation(self):
        """Test QueryAnalysis creation"""
        analysis = QueryAnalysis(
            query_type="read",
            complexity="simple",
            performance_issues=[],
            optimization_opportunities=[],
            index_recommendations=[],
            query_patterns=[],
            performance_characteristics="Good",
            best_practices=[],
            estimated_total_rows=0,
            estimated_db_hits=0
        )
        
        assert analysis.query_type == "read"
        assert analysis.complexity == "simple"
        assert analysis.performance_issues == []
        assert analysis.optimization_opportunities == []
        assert analysis.index_recommendations == []
        assert analysis.query_patterns == []
        assert analysis.performance_characteristics == "Good"
        assert analysis.best_practices == []
        assert analysis.estimated_total_rows == 0
        assert analysis.estimated_db_hits == 0


if __name__ == "__main__":
    pytest.main([__file__])
