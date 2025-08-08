#!/usr/bin/env python3
"""
Simple test script for the Neo4j Query Optimizer MCP Agent
"""

import json
import sys
import subprocess

def test_agent():
    """Test the MCP agent functionality"""
    
    print("🧪 Testing Neo4j Query Optimizer MCP Agent...")
    
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
    
    # Test 2: Test with a simple query (without Neo4j connection)
    print("\n2. Testing with simple query (no Neo4j connection)...")
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
                print("✅ Success! Agent responded (likely with connection error, which is expected)")
                print("   This is normal if Neo4j credentials aren't configured")
            else:
                print("❌ Unexpected response format")
                print(f"Response: {result.stdout}")
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing query analysis: {e}")
    
    print("\n🎉 Test completed!")
    print("\n📝 Next steps:")
    print("1. Configure your Neo4j credentials in your MCP client")
    print("2. Test with actual database connection")
    print("3. Use in Claude Desktop or other MCP clients")

if __name__ == "__main__":
    test_agent()
