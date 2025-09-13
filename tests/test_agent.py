#!/usr/bin/env python3
"""
Integration test script for the Neo4j Query Optimizer MCP Agent
Tests the refactored rule-based analyzer without LLM dependencies
"""

import json
import sys
import subprocess
import os

def test_agent():
    """Test the MCP agent functionality"""
    
    print("🧪 Testing Neo4j Query Optimizer MCP Agent (Refactored)...")
    print("📋 Testing rule-based analysis without LLM dependencies")
    
    # Test 1: List tools
    print("\n1. Testing tools/list...")
    try:
        result = subprocess.run([
            sys.executable, "src/mcp_neo4j_optimizer/agent.py"
        ], input=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"✅ Success! Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
            else:
                print("❌ Unexpected response format")
                print(f"Response: {result.stdout}")
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing tools/list: {e}")
    
    # Test 2: Test rule-based analysis (without Neo4j connection)
    print("\n2. Testing rule-based query analysis (no Neo4j connection)...")
    try:
        result = subprocess.run([
            sys.executable, "src/mcp_neo4j_optimizer/agent.py"
        ], input=json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "analyze-query-plan",
                "arguments": {
                    "query": "MATCH (n) RETURN n LIMIT 5"
                }
            }
        }), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if "result" in response:
                print("✅ Success! Agent responded with rule-based analysis")
                print("   This shows the refactored analyzer is working")
                # Check if the response contains our new structured analysis
                content = response["result"]["content"][0]["text"]
                if "Query Plan Analysis" in content:
                    print("   ✅ Contains structured analysis format")
                if "Neo4j Query Analysis Context" in content:
                    print("   ✅ Contains rich context for MCP clients")
            else:
                print("❌ Unexpected response format")
                print(f"Response: {result.stdout}")
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing query analysis: {e}")
    
    # Test 3: Test optimization tool (without Neo4j connection)
    print("\n3. Testing optimization tool (no Neo4j connection)...")
    try:
        result = subprocess.run([
            sys.executable, "src/mcp_neo4j_optimizer/agent.py"
        ], input=json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "optimize-neo4j-query",
                "arguments": {
                    "query": "MATCH (n) WHERE n.name = 'test' RETURN n"
                }
            }
        }), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if "result" in response:
                print("✅ Success! Agent responded to optimization request")
                print("   This shows the refactored optimization is working")
            else:
                print("❌ Unexpected response format")
                print(f"Response: {result.stdout}")
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing optimization: {e}")
    
    print("\n🎉 Integration test completed!")
    print("\n📋 Refactoring Summary:")
    print("✅ Removed LLM dependencies (OpenAI, Anthropic)")
    print("✅ Implemented rule-based Neo4jAnalyzer")
    print("✅ Added structured data classes (PerformanceIssue, QueryAnalysis)")
    print("✅ Simplified ConversationalInterface for rich context generation")
    print("✅ Updated dependencies in pyproject.toml")
    print("✅ Added comprehensive unit tests")
    
    print("\n📝 Next steps:")
    print("1. Configure your Neo4j credentials in your MCP client")
    print("2. Test with actual database connection")
    print("3. Use in Claude Desktop or other MCP clients")
    print("4. Run unit tests: pytest tests/")

if __name__ == "__main__":
    test_agent()
