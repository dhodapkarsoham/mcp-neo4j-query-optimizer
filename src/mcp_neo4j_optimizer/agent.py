#!/usr/bin/env python3
"""
Neo4j Query Optimizer Agent - MCP Server
Analyzes query plans, optimizes queries, and shows before/after comparisons.
"""

import json
import os
import sys
from typing import Dict, Any, Optional, List

from neo4j import GraphDatabase, basic_auth

# Neo4j credentials are loaded from Claude Desktop config env section
# No .env file loading needed

# Global variables
driver = None

class Neo4jOptimizerAgent:
    """Agent for Neo4j query optimization with plan comparison"""
    
    def __init__(self):
        try:
            self.setup_neo4j_connection()
        except Exception as e:
            print(f"⚠️  Neo4j connection not configured: {e}", file=sys.stderr)
            # Continue without connection for testing purposes
        
        # Optimization rules for generating better queries
        self.optimization_rules = {
            "MATCH (n) RETURN n": "MATCH (n:Label) WHERE n.property IS NOT NULL RETURN n LIMIT 100",
            "MATCH (n) WHERE": "Consider adding indexes on filtered properties",
            "MATCH (a)-[]->(b)": "Consider specifying relationship types: MATCH (a)-[:TYPE]->(b)",
            "ORDER BY": "Consider adding indexes on sorted properties",
            "CARTESIAN PRODUCT": "Add WHERE clause to join conditions"
        }
    
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
    
    def analyze_plan_issues(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze query plan for performance issues with comprehensive operator coverage"""
        issues = []
        
        def analyze_recursive(node, depth=0):
            # Get operator from operatorType field
            operator = node.get("operatorType", node.get("operator", ""))
            # Clean operator name (remove @neo4j suffix if present)
            clean_operator = operator.split("@")[0] if "@" in operator else operator
            estimated_rows = node.get("estimated_rows", 0)
            db_hits = node.get("db_hits", 0)
            
            # CRITICAL PERFORMANCE ISSUES
            if clean_operator == "AllNodesScan":
                issues.append({
                    "severity": "Critical",
                    "operator": operator,
                    "issue": "Full database scan - extremely expensive operation",
                    "suggestion": "Add labels (e.g., MATCH (n:Person)) or WHERE clauses to filter nodes before scanning",
                    "depth": depth,
                    "impact": "Scans entire database - very slow on large datasets"
                })
            
            elif clean_operator == "CartesianProduct":
                issues.append({
                    "severity": "Critical", 
                    "operator": operator,
                    "issue": "Cartesian product detected - missing join condition",
                    "suggestion": "Add WHERE clause to properly join nodes (e.g., WHERE a.id = b.id)",
                    "depth": depth,
                    "impact": "Exponential complexity - extremely expensive"
                })
            
            elif clean_operator == "DirectedAllRelationshipsScan":
                issues.append({
                    "severity": "Critical",
                    "operator": operator,
                    "issue": "Scanning all relationships in database",
                    "suggestion": "Specify relationship types (e.g., [:KNOWS]) or add node filters",
                    "depth": depth,
                    "impact": "Scans all relationships - very expensive"
                })
            
            # HIGH PERFORMANCE ISSUES
            elif clean_operator == "NodeByLabelScan":
                issues.append({
                    "severity": "High",
                    "operator": operator,
                    "issue": "Scanning all nodes with a specific label",
                    "suggestion": "Create indexes on properties used in WHERE clauses",
                    "depth": depth,
                    "impact": "Scans all nodes of a label - expensive on large labels"
                })
            
            elif clean_operator == "NodeIndexScan":
                issues.append({
                    "severity": "High",
                    "operator": operator,
                    "issue": "Scanning entire index instead of seeking",
                    "suggestion": "Use NodeIndexSeek by adding equality conditions on indexed properties",
                    "depth": depth,
                    "impact": "Scans entire index - less efficient than seeking"
                })
            
            elif clean_operator == "Expand":
                if estimated_rows > 10000:
                    issues.append({
                        "severity": "High",
                        "operator": operator,
                        "issue": f"Expanding many relationships ({estimated_rows} estimated)",
                        "suggestion": "Add relationship type filters or node property filters to reduce expansion",
                        "depth": depth,
                        "impact": "Expanding many relationships - expensive operation"
                    })
            
            # MEDIUM PERFORMANCE ISSUES
            elif clean_operator == "Filter":
                if estimated_rows > 10000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large filter operation ({estimated_rows} estimated rows)",
                        "suggestion": "Move filter conditions earlier in query or add indexes on filtered properties",
                        "depth": depth,
                        "impact": "Filtering large datasets after retrieval"
                    })
            
            elif clean_operator == "Sort":
                if estimated_rows > 1000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large sort operation ({estimated_rows} estimated rows)",
                        "suggestion": "Add indexes on sorted properties or use ORDER BY with LIMIT",
                        "depth": depth,
                        "impact": "Sorting large datasets in memory"
                    })
            
            elif clean_operator == "Aggregate":
                if estimated_rows > 10000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large aggregation ({estimated_rows} estimated rows)",
                        "suggestion": "Add WHERE clauses to reduce data before aggregation",
                        "depth": depth,
                        "impact": "Aggregating large datasets"
                    })
            
            elif clean_operator == "Unwind":
                if estimated_rows > 1000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large unwind operation ({estimated_rows} estimated rows)",
                        "suggestion": "Consider if unwinding is necessary or add LIMIT",
                        "depth": depth,
                        "impact": "Creating many rows from arrays"
                    })
            
            elif clean_operator == "Limit":
                if estimated_rows > 10000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large limit operation ({estimated_rows} estimated rows)",
                        "suggestion": "Add LIMIT earlier in query or use ORDER BY with LIMIT",
                        "depth": depth,
                        "impact": "Processing many rows before limiting"
                    })
            
            elif clean_operator == "Skip":
                if estimated_rows > 1000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large skip operation ({estimated_rows} estimated rows)",
                        "suggestion": "Consider using cursor-based pagination instead of SKIP",
                        "depth": depth,
                        "impact": "Skipping many rows is expensive"
                    })
            
            # JOIN OPERATORS
            elif clean_operator in ["NodeHashJoin", "NodeLeftHashJoin"]:
                if estimated_rows > 10000:
                    issues.append({
                        "severity": "Medium",
                        "operator": operator,
                        "issue": f"Large hash join ({estimated_rows} estimated rows)",
                        "suggestion": "Ensure proper indexes exist on join properties",
                        "depth": depth,
                        "impact": "Hash joining large datasets"
                    })
            
            elif clean_operator == "Apply":
                issues.append({
                    "severity": "Medium",
                    "operator": operator,
                    "issue": "Subquery execution detected",
                    "suggestion": "Consider rewriting as a single query or ensure subquery is optimized",
                    "depth": depth,
                    "impact": "Executing subqueries for each row"
                })
            
            # GENERAL PERFORMANCE CHECKS
            if db_hits > 10000:
                issues.append({
                    "severity": "High",
                    "operator": clean_operator,
                    "issue": f"High database hits ({db_hits}) for {operator}",
                    "suggestion": "Consider adding indexes or restructuring query",
                    "depth": depth,
                    "impact": "Many database operations - indicates expensive query"
                })
            
            # Analyze children
            for child in node.get("children", []):
                analyze_recursive(child, depth + 1)
        
        if plan:
            analyze_recursive(plan)
        
        return issues
    
    def generate_optimized_query(self, original_query: str, issues: List[Dict[str, Any]]) -> str:
        """Generate an optimized version of the query based on identified issues"""
        optimized = original_query.strip()
        
        # Check for critical issues first
        has_full_scan = any(issue["operator"] == "AllNodesScan" for issue in issues)
        has_cartesian = any(issue["operator"] == "CartesianProduct" for issue in issues)
        has_relationship_scan = any(issue["operator"] == "DirectedAllRelationshipsScan" for issue in issues)
        has_large_sort = any(issue["operator"] == "Sort" and issue["severity"] in ["High", "Medium"] for issue in issues)
        has_large_skip = any(issue["operator"] == "Skip" for issue in issues)
        
        # Add optimization comments
        optimization_comments = []
        
        if has_full_scan:
            optimization_comments.append("// OPTIMIZATION: Add labels to MATCH clauses (e.g., MATCH (n:Person))")
            # Replace full scans with label-based scans
            if "MATCH (n)" in optimized and ":" not in optimized.split("MATCH (n)")[1].split(")")[0]:
                optimized = optimized.replace("MATCH (n)", "MATCH (n:Label)")
            
            # Add filtering if none exists
            if "WHERE" not in optimized.upper():
                if "RETURN" in optimized:
                    return_part = optimized.split("RETURN")[0] + "WHERE n.id IS NOT NULL RETURN" + optimized.split("RETURN")[1]
                    optimized = return_part
        
        if has_cartesian:
            optimization_comments.append("// OPTIMIZATION: Add WHERE clause to join conditions (e.g., WHERE a.id = b.id)")
        
        if has_relationship_scan:
            optimization_comments.append("// OPTIMIZATION: Specify relationship types (e.g., [:KNOWS])")
        
        if has_large_sort:
            optimization_comments.append("// OPTIMIZATION: Consider adding indexes on sorted properties")
        
        if has_large_skip:
            optimization_comments.append("// OPTIMIZATION: Consider cursor-based pagination instead of SKIP")
        
        # Add LIMIT if missing and not a COUNT query
        if "LIMIT" not in optimized.upper() and "COUNT(" not in optimized.upper():
            optimized += " LIMIT 1000"
            optimization_comments.append("// OPTIMIZATION: Added LIMIT to prevent large result sets")
        
        # Prepend optimization comments
        if optimization_comments:
            optimized = "\n".join(optimization_comments) + "\n" + optimized
        
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
        }
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
        # Step 1: Get original query plan
        print("🔍 Analyzing original query...", file=sys.stderr)
        original_plan_data = agent.get_query_plan(query, database)
        original_issues = agent.analyze_plan_issues(original_plan_data["explain_plan"])
        
        # Step 2: Generate optimized query
        print("⚡ Generating optimized query...", file=sys.stderr)
        optimized_query = agent.generate_optimized_query(query, original_issues)
        
        # Step 3: Get optimized query plan
        print("📊 Analyzing optimized query...", file=sys.stderr)
        optimized_plan_data = agent.get_query_plan(optimized_query, database)
        optimized_issues = agent.analyze_plan_issues(optimized_plan_data["explain_plan"])
        
        # Step 4: Compare plans
        comparison = agent.compare_plans(
            original_plan_data["explain_plan"],
            optimized_plan_data["explain_plan"]
        )
        
        # Format comprehensive response
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

### Performance Issues Found:
"""
        
        if original_issues:
            for issue in original_issues:
                impact_info = f"- Impact: {issue.get('impact', 'Performance impact')}" if 'impact' in issue else ""
                response += f"""
**{issue['severity']} - {issue['operator']}**
- Issue: {issue['issue']}
- Suggestion: {issue['suggestion']}
- Depth: {issue['depth']}
{impact_info}
"""
        else:
            response += "\n✅ No major performance issues detected\n"
        
        response += f"""
### Original Plan Operators:
{chr(10).join(f"- **{op}**: {count}" for op, count in comparison['original_operators'].items())}

## 📊 Optimized Query Plan Analysis
**Estimated Total Rows**: {comparison['optimized_estimated_rows']:,}

### Performance Issues Remaining:
"""
        
        if optimized_issues:
            for issue in optimized_issues:
                impact_info = f"- Impact: {issue.get('impact', 'Performance impact')}" if 'impact' in issue else ""
                response += f"""
**{issue['severity']} - {issue['operator']}**
- Issue: {issue['issue']}
- Suggestion: {issue['suggestion']}
- Depth: {issue['depth']}
{impact_info}
"""
        else:
            response += "\n✅ No major performance issues detected\n"
        
        response += f"""
### Optimized Plan Operators:
{chr(10).join(f"- **{op}**: {count}" for op, count in comparison['optimized_operators'].items())}

## 🎯 Improvements Made:
{chr(10).join(comparison['improvements'])}

## 📈 Performance Comparison:
- **Row Estimation Change**: {comparison['original_estimated_rows']:,} → {comparison['optimized_estimated_rows']:,}
- **Issues Resolved**: {len(original_issues) - len(optimized_issues)} out of {len(original_issues)}

## 💡 Next Steps:
1. Test the optimized query with your actual data
2. Consider creating suggested indexes for better performance
3. Monitor query execution times in production
4. Adjust LIMIT values based on your actual needs
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
        plan_data = agent.get_query_plan(query, database)
        issues = agent.analyze_plan_issues(plan_data["explain_plan"])
        
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
"""
        
        if issues:
            for issue in issues:
                impact_info = f"- **Impact**: {issue.get('impact', 'Performance impact')}" if 'impact' in issue else ""
                response += f"""
### {issue['severity']} Issue - {issue['operator']}
- **Problem**: {issue['issue']}
- **Suggestion**: {issue['suggestion']}
- **Location**: Depth {issue['depth']} in execution plan
{impact_info}
"""
        else:
            response += "\n✅ No major performance issues detected"
        
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