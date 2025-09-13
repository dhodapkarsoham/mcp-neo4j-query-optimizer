#!/usr/bin/env python3


"""
Neo4j Query Optimizer Agent - MCP Server
Analyzes query plans, optimizes queries, and shows before/after comparisons.
Provides rich, structured analysis for MCP clients to interpret intelligently.
"""

import json
import os
import sys
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from neo4j import GraphDatabase, basic_auth

# Neo4j credentials are loaded from MCP client config env section
# No .env file loading needed

# Global variables
driver = None

class Severity(Enum):
    """Performance issue severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

@dataclass
class PerformanceIssue:
    """Represents a performance issue found in query analysis"""
    severity: Severity
    operator: str
    issue: str
    suggestion: str
    impact: str
    depth: int
    estimated_rows: Optional[int] = None
    db_hits: Optional[int] = None

@dataclass
class QueryAnalysis:
    """Comprehensive query analysis results"""
    query_type: str
    complexity: str
    performance_issues: List[PerformanceIssue]
    optimization_opportunities: List[str]
    index_recommendations: List[str]
    query_patterns: List[str]
    performance_characteristics: str
    best_practices: List[str]
    estimated_total_rows: int
    estimated_db_hits: int

class Neo4jAnalyzer:
    """Neo4j query analyzer that extracts structured operator data for MCP clients to interpret"""
    
    def __init__(self):
        print("✅ Neo4j analyzer initialized for structured data extraction", file=sys.stderr)
    
    def analyze_operators(self, operators: List[Dict], query: str) -> List[Dict[str, Any]]:
        """Extract structured operator data for MCP client interpretation"""
        operator_data = []
        
        for op in operators:
            operator = op.get("operator", "Unknown")
            clean_operator = operator.split("@")[0] if "@" in operator else operator
            estimated_rows = op.get("estimated_rows", 0)
            db_hits = op.get("db_hits", 0)
            depth = op.get("depth", 0)
            args = op.get("args", {})
            identifiers = op.get("identifiers", [])
            
            # Extract operator characteristics for MCP client analysis
            operator_info = {
                "operator": operator,
                "clean_operator": clean_operator,
                "estimated_rows": estimated_rows,
                "db_hits": db_hits,
                "depth": depth,
                "args": args,
                "identifiers": identifiers,
                "is_leaf": self._is_leaf_operator(clean_operator),
                "is_updating": self._is_updating_operator(clean_operator),
                "is_eager": self._is_eager_operator(clean_operator),
                "performance_characteristics": self._get_operator_characteristics(clean_operator, estimated_rows, db_hits)
            }
            
            operator_data.append(operator_info)
        
        return operator_data
    
    def _is_leaf_operator(self, operator: str) -> bool:
        """Determine if operator is a leaf operator based on Neo4j documentation"""
        leaf_operators = {
            "AllNodesScan", "Argument", "ArgumentTracker", "AssertingMultiNodeIndexSeek",
            "AssertingMultiRelationshipIndexSeek", "AssertingSingleNodeIndexSeek",
            "AssertingSingleRelationshipIndexSeek", "DirectedAllRelationshipsScan",
            "DirectedRelationshipByElementIdSeek", "DirectedRelationshipByIdSeek",
            "DirectedRelationshipIndexContainsScan", "DirectedRelationshipIndexEndsWithScan",
            "DirectedRelationshipIndexScan", "DirectedRelationshipIndexSeek",
            "DirectedRelationshipIndexSeekByRange", "DirectedRelationshipTypeScan",
            "DirectedUnionRelationshipTypesScan", "NodeByElementIdSeek", "NodeByIdSeek",
            "NodeByLabelScan", "NodeIndexContainsScan", "NodeIndexEndsWithScan",
            "NodeIndexScan", "NodeIndexSeek", "NodeIndexSeekByRange", "NodeUniqueIndexSeek",
            "NodeUniqueIndexSeekByRange", "UndirectedAllRelationshipsScan",
            "UndirectedRelationshipByElementIdSeek", "UndirectedRelationshipByIdSeek",
            "UndirectedRelationshipIndexContainsScan", "UndirectedRelationshipIndexEndsWithScan",
            "UndirectedRelationshipIndexScan", "UndirectedRelationshipIndexSeek",
            "UndirectedRelationshipIndexSeekByRange", "UndirectedRelationshipTypeScan",
            "UndirectedUnionRelationshipTypesScan", "UnionNodeByLabelsScan"
        }
        return operator in leaf_operators
    
    def _is_updating_operator(self, operator: str) -> bool:
        """Determine if operator is an updating operator"""
        updating_operators = {
            "Create", "Delete", "MergeCreateNode", "MergeCreateRelationship",
            "RemoveLabels", "SetLabels", "SetNodeProperties", "SetNodeProperty",
            "SetProperties", "SetProperty", "SetRelationshipProperties", "SetRelationshipProperty"
        }
        return operator in updating_operators
    
    def _is_eager_operator(self, operator: str) -> bool:
        """Determine if operator is an eager operator"""
        eager_operators = {
            "EagerAggregation", "EagerLimit", "EagerSort", "EagerUnion",
            "ValueHashJoin", "CartesianProduct"
        }
        return operator in eager_operators or "Eager" in operator
    
    def _get_operator_characteristics(self, operator: str, estimated_rows: int, db_hits: int) -> Dict[str, Any]:
        """Extract performance characteristics for MCP client analysis"""
        characteristics = {
            "operator_type": operator,
            "estimated_rows": estimated_rows,
            "db_hits": db_hits,
            "performance_indicators": []
        }
        
        # Add performance indicators based on operator type and metrics
        if estimated_rows > 100000:
            characteristics["performance_indicators"].append("high_row_count")
        if db_hits > 10000:
            characteristics["performance_indicators"].append("high_db_hits")
        if operator in ["AllNodesScan", "UndirectedAllRelationshipsScan"]:
            characteristics["performance_indicators"].append("full_scan")
        if operator in ["CartesianProduct"]:
            characteristics["performance_indicators"].append("cartesian_product")
        if "Index" in operator:
            characteristics["performance_indicators"].append("index_usage")
        if "Eager" in operator:
            characteristics["performance_indicators"].append("eager_operation")
        
        return characteristics
    
    def analyze_query(self, query: str, operators: List[Dict] = None) -> Dict[str, Any]:
        """Extract comprehensive structured query data for MCP client analysis"""
        if operators is None:
            operators = []
        
        # Extract structured operator data
        operator_data = self.analyze_operators(operators, query)
        
        # Classify query type and complexity
        query_type = self._classify_query_type(query)
        complexity = self._assess_query_complexity(query)
        
        # Identify patterns and characteristics
        query_patterns = self._identify_query_patterns(query)
        performance_characteristics = self._analyze_performance_characteristics(query)
        
        # Calculate totals
        estimated_total_rows = sum(op.get("estimated_rows", 0) for op in operators)
        estimated_db_hits = sum(op.get("db_hits", 0) for op in operators)
        
        # Return structured data for MCP client interpretation
        return {
            "query": query,
            "query_type": query_type,
            "complexity": complexity,
            "query_patterns": query_patterns,
            "performance_characteristics": performance_characteristics,
            "operators": operator_data,
            "summary": {
                "total_operators": len(operator_data),
                "leaf_operators": len([op for op in operator_data if op["is_leaf"]]),
                "updating_operators": len([op for op in operator_data if op["is_updating"]]),
                "eager_operators": len([op for op in operator_data if op["is_eager"]]),
                "estimated_total_rows": estimated_total_rows,
                "estimated_db_hits": estimated_db_hits
            },
            "performance_indicators": self._extract_performance_indicators(operator_data),
            "query_metadata": {
                "has_where_clause": "WHERE" in query,
                "has_order_by": "ORDER BY" in query,
                "has_limit": "LIMIT" in query,
                "has_aggregation": any(func in query.upper() for func in ["COUNT(", "SUM(", "AVG(", "MIN(", "MAX("]),
                "has_relationships": "-[" in query and "]->" in query
            }
        }
    
    def _extract_performance_indicators(self, operator_data: List[Dict]) -> List[str]:
        """Extract overall performance indicators from operator data"""
        indicators = set()
        
        for op in operator_data:
            indicators.update(op["performance_characteristics"]["performance_indicators"])
        
        return list(indicators)
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_upper = query.upper()
        if "CREATE" in query_upper:
            return "write"
        elif "DELETE" in query_upper or "REMOVE" in query_upper:
            return "delete"
        elif "SET" in query_upper or "MERGE" in query_upper:
            return "update"
        elif "MATCH" in query_upper and "RETURN" in query_upper:
            return "read"
        else:
            return "unknown"
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess query complexity based on patterns"""
        complexity_score = 0
        
        # Basic patterns
        if "MATCH" in query:
            complexity_score += 1
        if "WHERE" in query:
            complexity_score += 1
        if "ORDER BY" in query:
            complexity_score += 1
        if "LIMIT" in query:
            complexity_score += 1
        
        # Advanced patterns
        if "COUNT(" in query or "SUM(" in query or "AVG(" in query:
            complexity_score += 2
        if "UNION" in query.upper():
            complexity_score += 2
        if "CASE" in query.upper():
            complexity_score += 1
        if "WITH" in query.upper():
            complexity_score += 1
        
        # Relationship complexity
        relationship_count = len(re.findall(r'\[.*?\]', query))
        complexity_score += min(relationship_count, 3)  # Cap at 3
        
        if complexity_score <= 2:
            return "simple"
        elif complexity_score <= 5:
            return "medium"
        else:
            return "complex"
    
    def _identify_query_patterns(self, query: str) -> List[str]:
        """Identify query patterns for context"""
        patterns = []
        
        if "MATCH (" in query:
            patterns.append("node matching")
        
        if "-[" in query and "]->" in query:
            patterns.append("relationship traversal")
        
        if "WHERE" in query:
            patterns.append("property filtering")
        
        if "ORDER BY" in query:
            patterns.append("result sorting")
        
        if "LIMIT" in query:
            patterns.append("result limiting")
        
        if "COUNT(" in query or "SUM(" in query or "AVG(" in query:
            patterns.append("aggregation")
        
        if "UNION" in query.upper():
            patterns.append("query union")
        
        if "WITH" in query.upper():
            patterns.append("query chaining")
        
        return patterns
    
    def _analyze_performance_characteristics(self, query: str) -> str:
        """Analyze performance characteristics of the query"""
        characteristics = []
        
        if "MATCH (n)" in query and ":" not in query:
            characteristics.append("Full database scan - will be slow on large datasets")
        
        if "WHERE" not in query:
            characteristics.append("No filtering - may return large result sets")
        
        if "LIMIT" not in query:
            characteristics.append("No result limiting - potential for memory issues")
        
        if "ORDER BY" in query:
            characteristics.append("Sorting operation - consider indexes on sorted properties")
        
        if "COUNT(" in query or "SUM(" in query:
            characteristics.append("Aggregation operation - may be memory intensive")
        
        if "UNION" in query.upper():
            characteristics.append("Query union - multiple result sets combined")
        
        return "; ".join(characteristics) if characteristics else "Query appears well-structured"
    

class ConversationalInterface:
    """Generates structured context for MCP clients to interpret Neo4j query analysis"""
    
    def __init__(self, analyzer: Neo4jAnalyzer):
        self.analyzer = analyzer
    
    def generate_rich_context(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate structured context for MCP clients to interpret and discuss"""
        context = f"""# Neo4j Query Analysis - Structured Data for MCP Client

## Query Information
- **Query**: {analysis['query']}
- **Type**: {analysis['query_type']} query
- **Complexity**: {analysis['complexity']}
- **Patterns**: {', '.join(analysis['query_patterns'])}

## Execution Plan Summary
- **Total Operators**: {analysis['summary']['total_operators']}
- **Leaf Operators**: {analysis['summary']['leaf_operators']}
- **Updating Operators**: {analysis['summary']['updating_operators']}
- **Eager Operators**: {analysis['summary']['eager_operators']}
- **Estimated Total Rows**: {analysis['summary']['estimated_total_rows']:,}
- **Estimated DB Hits**: {analysis['summary']['estimated_db_hits']:,}

## Performance Indicators
{chr(10).join([f"- {indicator}" for indicator in analysis['performance_indicators']])}

## Query Metadata
- **Has WHERE clause**: {analysis['query_metadata']['has_where_clause']}
- **Has ORDER BY**: {analysis['query_metadata']['has_order_by']}
- **Has LIMIT**: {analysis['query_metadata']['has_limit']}
- **Has Aggregation**: {analysis['query_metadata']['has_aggregation']}
- **Has Relationships**: {analysis['query_metadata']['has_relationships']}

## Operator Details
{self._format_operator_details(analysis['operators'])}

## Performance Characteristics
{analysis['performance_characteristics']}

## MCP Client Instructions
Based on this structured data and your knowledge of Neo4j operators from the official documentation, provide:
1. Performance analysis and recommendations
2. Optimization suggestions
3. Index recommendations
4. Query rewrite suggestions
5. Before/after comparisons

Reference: https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/
"""
        return context
    
    def _format_operator_details(self, operators: List[Dict]) -> str:
        """Format operator details for context"""
        if not operators:
            return "No operators found"
        
        details = []
        for i, op in enumerate(operators, 1):
            details.append(f"""
### Operator {i}: {op['operator']}
- **Type**: {op['clean_operator']}
- **Estimated Rows**: {op['estimated_rows']:,}
- **DB Hits**: {op['db_hits']:,}
- **Depth**: {op['depth']}
- **Is Leaf**: {op['is_leaf']}
- **Is Updating**: {op['is_updating']}
- **Is Eager**: {op['is_eager']}
- **Performance Indicators**: {', '.join(op['performance_characteristics']['performance_indicators'])}
""")
        
        return '\n'.join(details)

class Neo4jOptimizerAgent:
    """Agent for Neo4j query optimization with plan comparison"""
    
    def __init__(self):
        try:
            self.setup_neo4j_connection()
        except Exception as e:
            print(f"⚠️  Neo4j connection not configured: {e}", file=sys.stderr)
            # Continue without connection for testing purposes
        
        # Initialize analyzer
        self.analyzer = Neo4jAnalyzer()
        
        # Initialize conversational interface
        self.conversational_interface = ConversationalInterface(self.analyzer)
    
    def setup_neo4j_connection(self):
        """Initialize Neo4j connection"""
        global driver
        try:
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            
            if neo4j_uri and neo4j_password:
                driver = GraphDatabase.driver(
                    neo4j_uri,
                    auth=basic_auth(neo4j_user, neo4j_password)
                )
                # Test connection
                with driver.session() as session:
                    session.run("RETURN 1 as test").consume()
                print("✅ Neo4j connection established", file=sys.stderr)
            else:
                print("⚠️  Neo4j connection not configured", file=sys.stderr)
                raise Exception("Neo4j credentials not found")
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}", file=sys.stderr)
            raise
    
    def get_query_plan(self, query: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed query execution plan from Neo4j"""
        if not driver:
            raise Exception("Neo4j connection not available")
        
        try:
            with driver.session(database=database) as session:
                # Get EXPLAIN plan
                explain_result = session.run(f"EXPLAIN {query}")
                explain_plan = explain_result.consume().plan
                
                # Get PROFILE plan (with execution stats)
                try:
                    profile_result = session.run(f"PROFILE {query}")
                    profile_plan = profile_result.consume().plan
                    profile_summary = profile_result.consume().result_summary
                    
                    return {
                        "explain_plan": self._plan_to_dict(explain_plan),
                        "profile_plan": self._plan_to_dict(profile_plan),
                        "execution_time": profile_summary.result_available_after,
                        "query": query
                    }
                except Exception:
                    # If PROFILE fails, return just EXPLAIN
                    return {
                        "explain_plan": self._plan_to_dict(explain_plan),
                        "profile_plan": None,
                        "execution_time": None,
                        "query": query
                    }
        except Exception as e:
            raise Exception(f"Failed to get query plan: {str(e)}")
    
    def _plan_to_dict(self, plan) -> Dict[str, Any]:
        """Convert Neo4j plan to dictionary"""
        if not plan:
            return {}
        
        # Handle both plan objects and dictionaries
        if hasattr(plan, 'operator_type'):
            # Neo4j plan object
            result = {
                "operator": plan.operator_type,
                "args": dict(plan.arguments) if hasattr(plan, 'arguments') else {},
                "estimated_rows": getattr(plan, 'arguments', {}).get("EstimatedRows", 0),
                "identifiers": getattr(plan, 'identifiers', []),
                "children": []
            }
            
            for child in getattr(plan, 'children', []):
                result["children"].append(self._plan_to_dict(child))
        else:
            # Already a dictionary
            result = plan if isinstance(plan, dict) else {}
        
        return result
    
    def analyze_plan_issues(self, plan: Dict[str, Any], query: str = "") -> List[Dict[str, Any]]:
        """Extract structured operator data from query plan"""
        # Extract operators from plan
        operators = self._extract_operators_from_plan(plan)
        
        # Return structured operator data
        return self.analyzer.analyze_operators(operators, query)
    
    def _extract_operators_from_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract operator information from query plan for analysis"""
        operators = []
        
        def extract_recursive(node, depth=0):
            if not node:
                return
            
            # Get operator from operatorType field
            operator = node.get("operatorType", node.get("operator", ""))
            estimated_rows = node.get("estimated_rows", 0)
            db_hits = node.get("db_hits", 0)
            args = node.get("args", {})
            
            operators.append({
                    "operator": operator,
                "estimated_rows": estimated_rows,
                "db_hits": db_hits,
                    "depth": depth,
                "args": args,
                "identifiers": node.get("identifiers", [])
            })
            
            # Recursively extract from children
            for child in node.get("children", []):
                extract_recursive(child, depth + 1)
        
        if plan:
            extract_recursive(plan)
        
        return operators
    
    def generate_optimized_query(self, original_query: str, operator_data: List[Dict[str, Any]]) -> str:
        """Generate an optimized version of the query based on operator analysis"""
        # For now, return the original query with basic optimizations
        # The MCP client should handle the intelligent optimization based on operator data
        optimized = original_query.strip()
        
        # Basic optimizations that are generally safe
        if "MATCH (n)" in optimized and ":" not in optimized:
            optimized = optimized.replace("MATCH (n)", "MATCH (n:Node)")
        
        if "LIMIT" not in optimized.upper() and "COUNT(" not in optimized.upper():
            optimized += " LIMIT 1000"
        
        return optimized
    
    def compare_plans(self, original_plan: Dict[str, Any], optimized_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two query plans and highlight improvements"""
        
        def count_operators(plan, operator_counts=None):
            if operator_counts is None:
                operator_counts = {}
            
            if plan:
                op = plan.get("operator", "Unknown")
                operator_counts[op] = operator_counts.get(op, 0) + 1
                
                for child in plan.get("children", []):
                    count_operators(child, operator_counts)
            
            return operator_counts
        
        def estimate_total_rows(plan):
            if not plan:
                return 0
            total = plan.get("estimated_rows", 0)
            for child in plan.get("children", []):
                total += estimate_total_rows(child)
            return total
        
        original_ops = count_operators(original_plan)
        optimized_ops = count_operators(optimized_plan)
        
        return {
            "original_operators": original_ops,
            "optimized_operators": optimized_ops,
            "original_estimated_rows": estimate_total_rows(original_plan),
            "optimized_estimated_rows": estimate_total_rows(optimized_plan),
            "improvements": self._identify_improvements(original_ops, optimized_ops)
        }
    
    def _identify_improvements(self, original_ops: Dict, optimized_ops: Dict) -> List[str]:
        """Identify specific improvements between plans"""
        improvements = []
        
        # Check for removed expensive operations
        if original_ops.get("AllNodesScan", 0) > optimized_ops.get("AllNodesScan", 0):
            improvements.append("✅ Reduced full database scans")
        
        if original_ops.get("CartesianProduct", 0) > optimized_ops.get("CartesianProduct", 0):
            improvements.append("✅ Eliminated cartesian products")
        
        if original_ops.get("DirectedAllRelationshipsScan", 0) > optimized_ops.get("DirectedAllRelationshipsScan", 0):
            improvements.append("✅ Reduced relationship scans")
        
        # Check for added beneficial operations
        if optimized_ops.get("NodeByLabelScan", 0) > original_ops.get("NodeByLabelScan", 0):
            improvements.append("✅ Added efficient label-based scans")
        
        if optimized_ops.get("NodeIndexScan", 0) > original_ops.get("NodeIndexScan", 0):
            improvements.append("✅ Utilized index scans")
        
        if optimized_ops.get("Limit", 0) > original_ops.get("Limit", 0):
            improvements.append("✅ Added result limiting")
        
        if not improvements:
            improvements.append("ℹ️  Query structure maintained with minor optimizations")
        
        return improvements

# MCP Server Implementation
agent = Neo4jOptimizerAgent()

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC request"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    try:
        if method == "initialize":
            return handle_initialize(params, request_id)
        elif method == "tools/list":
            return list_tools(request_id)
        elif method == "tools/call":
            return call_tool(params, request_id)
        else:
            return error_response(request_id, f"Unknown method: {method}")
    except Exception as e:
        return error_response(request_id, str(e))

def handle_initialize(params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
    """Handle MCP initialize request"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "neo4j-optimizer-agent",
                "version": "2.0.0"
            }
        }
    }

def list_tools(request_id: Any) -> Dict[str, Any]:
    """List available tools"""
    tools = [
        {
            "name": "optimize-neo4j-query",
            "description": "Analyze a Neo4j query, optimize it, and compare the before/after query plans to show improvements",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Cypher query to analyze and optimize"
                    },
                    "database": {
                        "type": "string",
                        "description": "Optional database name (defaults to current database)"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "analyze-query-plan",
            "description": "Get detailed query plan analysis for a Cypher query without optimization",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Cypher query to analyze"
                    },
                    "database": {
                        "type": "string",
                        "description": "Optional database name"
                    }
                },
                "required": ["query"]
            }
        },
    ]
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": tools}
    }

def call_tool(params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
    """Call a specific tool"""
    name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        if name == "optimize-neo4j-query":
            result = optimize_neo4j_query(arguments)
        elif name == "analyze-query-plan":
            result = analyze_query_plan_only(arguments)
        else:
            return error_response(request_id, f"Unknown tool: {name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": result}]
            }
        }
    except Exception as e:
        return error_response(request_id, str(e))

def optimize_neo4j_query(arguments: Dict[str, Any]) -> str:
    """Main optimization function - analyzes original, creates optimized version, compares plans"""
    query = arguments.get("query")
    database = arguments.get("database")
    
    if not query:
        raise ValueError("Query is required")
    
    try:
        # Initialize agent
        agent = Neo4jOptimizerAgent()
        
        # Step 1: Get original query plan
        print("🔍 Analyzing original query...", file=sys.stderr)
        original_plan_data = agent.get_query_plan(query, database)
        original_operator_data = agent.analyze_plan_issues(original_plan_data["explain_plan"], query)
        
        # Step 2: Generate optimized query
        print("⚡ Generating optimized query...", file=sys.stderr)
        optimized_query = agent.generate_optimized_query(query, original_operator_data)
        
        # Step 3: Get optimized query plan
        print("📊 Analyzing optimized query...", file=sys.stderr)
        optimized_plan_data = agent.get_query_plan(optimized_query, database)
        optimized_operator_data = agent.analyze_plan_issues(optimized_plan_data["explain_plan"], optimized_query)
        
        # Step 4: Compare plans
        comparison = agent.compare_plans(
            original_plan_data["explain_plan"],
            optimized_plan_data["explain_plan"]
        )
        
        # Step 5: Generate comprehensive analysis
        original_analysis = agent.analyzer.analyze_query(query, agent._extract_operators_from_plan(original_plan_data["explain_plan"]))
        
        # Format comprehensive response with structured data
        response = f"""# Neo4j Query Optimization Analysis

## 📝 Original Query
```cypher
{query}
```

## ⚡ Optimized Query  
```cypher
{optimized_query}
```

## 🔍 Original Query Plan Analysis
**Execution Time**: {original_plan_data['execution_time'] or 'N/A'}ms
**Estimated Total Rows**: {comparison['original_estimated_rows']:,}

### Original Plan Operators:
{chr(10).join(f"- **{op}**: {count}" for op, count in comparison['original_operators'].items())}

## 📊 Optimized Query Plan Analysis
**Estimated Total Rows**: {comparison['optimized_estimated_rows']:,}

### Optimized Plan Operators:
{chr(10).join(f"- **{op}**: {count}" for op, count in comparison['optimized_operators'].items())}

## 🎯 Improvements Made:
{chr(10).join(comparison['improvements'])}

## 📈 Performance Comparison:
- **Row Estimation Change**: {comparison['original_estimated_rows']:,} → {comparison['optimized_estimated_rows']:,}

## 💡 Next Steps:
1. Test the optimized query with your actual data
2. Consider creating suggested indexes for better performance
3. Monitor query execution times in production
4. Adjust LIMIT values based on your actual needs

## 🗣️ Structured Data for MCP Client Analysis
{agent.conversational_interface.generate_rich_context(query, original_analysis)}
"""
        
        return response
        
    except Exception as e:
        return f"❌ Error during optimization: {str(e)}"

def analyze_query_plan_only(arguments: Dict[str, Any]) -> str:
    """Analyze query plan without optimization"""
    query = arguments.get("query")
    database = arguments.get("database")
    
    if not query:
        raise ValueError("Query is required")
    
    try:
        # Initialize agent
        agent = Neo4jOptimizerAgent()
        
        plan_data = agent.get_query_plan(query, database)
        operator_data = agent.analyze_plan_issues(plan_data["explain_plan"], query)
        
        # Generate comprehensive analysis
        analysis = agent.analyzer.analyze_query(query, agent._extract_operators_from_plan(plan_data["explain_plan"]))
        
        response = f"""# Query Plan Analysis

## Query
```cypher
{query}
```

## Execution Plan
**Execution Time**: {plan_data['execution_time'] or 'N/A'}ms

### Plan Structure
```json
{json.dumps(plan_data['explain_plan'], indent=2)}
```

## Performance Analysis
**Total Operators**: {analysis['summary']['total_operators']}
**Leaf Operators**: {analysis['summary']['leaf_operators']}
**Eager Operators**: {analysis['summary']['eager_operators']}
**Estimated Total Rows**: {analysis['summary']['estimated_total_rows']:,}
**Estimated DB Hits**: {analysis['summary']['estimated_db_hits']:,}

### Performance Indicators
{chr(10).join([f"- {indicator}" for indicator in analysis['performance_indicators']])}

## 🗣️ Structured Data for MCP Client Analysis
{agent.conversational_interface.generate_rich_context(query, analysis)}
"""
        
        return response
        
    except Exception as e:
        return f"❌ Error analyzing query: {str(e)}"

def error_response(request_id: Any, error_message: str) -> Dict[str, Any]:
    """Create error response"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32603,
            "message": error_message
        }
    }

def main():
    """Main entry point"""
    print("🚀 Neo4j Optimizer Agent starting...", file=sys.stderr)
    print("📝 Send JSON-RPC requests to stdin", file=sys.stderr)
    
    # Read JSON-RPC requests from stdin
    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue
                
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            error_resp = error_response(None, "Parse error")
            print(json.dumps(error_resp))
            sys.stdout.flush()
        except Exception as e:
            error_resp = error_response(None, str(e))
            print(json.dumps(error_resp))
            sys.stdout.flush()

if __name__ == "__main__":
    main()