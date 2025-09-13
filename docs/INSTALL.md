# 🚀 Installation Guide for MCP Neo4j Query Optimizer

This guide will help you install and configure the MCP Neo4j Query Optimizer server for use with Claude Desktop and other MCP clients.

## 📋 Prerequisites

- Python 3.8 or higher
- MCP client (Claude Desktop, etc.)
- Neo4j database (optional - works in rule-based mode without it)

## 🔧 Installation Methods

### Method 1: Install from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/mcp-neo4j-query-optimizer.git
   cd mcp-neo4j-query-optimizer
   ```

2. **Install dependencies**:
   ```bash
   pip install neo4j python-dotenv
   ```

### Method 2: Install via pip (when published)

```bash
pip install mcp-neo4j-query-optimizer
```

## ⚙️ Configuration

### 1. MCP Client Configuration

The MCP server works with or without Neo4j credentials:

**With Neo4j credentials** (for live database analysis):
```json
{
  "mcpServers": {
    "neo4j-query-optimizer": {
      "command": "/path/to/python",
      "args": ["/path/to/your/src/mcp_neo4j_optimizer/agent.py"],
      "env": {
        "NEO4J_URI": "neo4j+s://your-db-id.databases.neo4j.io",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

**Without Neo4j credentials** (rule-based analysis mode):
```json
{
  "mcpServers": {
    "neo4j-query-optimizer": {
      "command": "/path/to/python",
      "args": ["/path/to/your/src/mcp_neo4j_optimizer/agent.py"]
    }
  }
}
```

### 2. Configuration File Locations

**For Claude Desktop**:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**For Other MCP Clients**:
Use the configuration from `examples/mcp-neo4j-query-optimizer.json` as a template.

### 3. Important Configuration Notes

- **Python Path**: Use the full path to your Python executable
- **Script Path**: Use the full path to the `agent.py` file
- **Neo4j Credentials**: Optional - the server works without them
- **File Permissions**: Ensure the script is executable: `chmod +x src/mcp_neo4j_optimizer/agent.py`

## 🧪 Testing the Installation

### 1. Test the MCP Server Directly

```bash
# Test the server
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python src/mcp_neo4j_optimizer/agent.py
```

### 2. Test with a Simple Query

```bash
# Test optimization
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "optimize-neo4j-query", "arguments": {"query": "MATCH (n) RETURN n LIMIT 5"}}}' | python src/mcp_neo4j_optimizer/agent.py
```

### 3. Test in Claude Desktop

1. Restart Claude Desktop completely
2. Start a new conversation
3. Try: `"Can you analyze this query using the neo4j-query-optimizer: MATCH (n) RETURN n LIMIT 10"`

## 🛠️ Available Tools

Once installed, you'll have access to these tools:

### 1. `optimize-neo4j-query`
Analyze and optimize a Cypher query.

**Parameters:**
- `query` (required): The Cypher query to analyze
- `database` (optional): Database name

**Example:**
```json
{
  "query": "MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10"
}
```

### 2. `analyze-query-plan`
Get detailed structured analysis of a query execution plan.

**Parameters:**
- `query` (required): The Cypher query to analyze
- `database` (optional): Database name

**Example:**
```json
{
  "query": "MATCH (n:Person) WHERE n.age > 30 RETURN n"
}
```

## 🔍 Usage Examples

### In Claude Desktop

1. **Optimize a query**:
   ```
   Can you optimize this Cypher query using the neo4j-query-optimizer: MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10
   ```

2. **Analyze query plan**:
   ```
   Can you analyze this query plan using the neo4j-query-optimizer: MATCH (n:Person) WHERE n.age > 30 RETURN n
   ```

3. **Direct tool usage**:
   ```
   @neo4j-query-optimizer analyze-query-plan "MATCH (n:Person) WHERE n.age > 30 RETURN n"
   ```

### Direct API Usage

```python
import asyncio
from mcp import ClientSession

async def test_optimizer():
    async with ClientSession.create_stdio(["mcp-neo4j-query-optimizer"]) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[t.name for t in tools.tools]}")
        
        # Optimize a query
        result = await session.call_tool(
            "optimize-query",
            {"query": "MATCH (n) RETURN n LIMIT 5"}
        )
        print(result.content[0].text)

asyncio.run(test_optimizer())
```

## 🐛 Troubleshooting

### Common Issues

1. **"Command not found"**
   - Ensure the package is installed: `pip install -e .`
   - Check PATH: `which mcp-neo4j-query-optimizer`

2. **Neo4j connection failed**
   - Verify your `.env` file has correct credentials
   - Test connection: `python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt+s://your-uri', auth=('neo4j', 'password')); print('Connected!')"`

3. **MCP client can't find server**
   - Check the command path in your MCP configuration
   - Ensure environment variables are set correctly

### Debug Mode

Run with debug output:

```bash
NEO4J_DEBUG=1 mcp-neo4j-query-optimizer
```

### Logs

Check for error messages in:
- MCP client logs
- Python console output
- Neo4j database logs

## 🔧 Troubleshooting

### Common Issues

**1. MCP Server Not Loading**
- **Problem**: Claude Desktop shows "No tools available"
- **Solution**: 
  - Check that the Python path in your configuration is correct
  - Ensure the script path points to the actual `agent.py` file
  - Verify the script is executable: `chmod +x src/mcp_neo4j_optimizer/agent.py`
  - Restart Claude Desktop completely

**2. Configuration Errors**
- **Problem**: JSON syntax errors in configuration
- **Solution**: 
  - Validate your JSON configuration with a JSON validator
  - Check for missing commas or brackets
  - Ensure proper escaping of paths with spaces

**3. Python Path Issues**
- **Problem**: "Command not found" or "No module named" errors
- **Solution**: 
  - Use the full path to your Python executable
  - Install required dependencies: `pip install neo4j python-dotenv`
  - Ensure you're using the correct Python environment

**4. Neo4j Connection Issues**
- **Problem**: Neo4j connection failures
- **Solution**: 
  - The MCP server works without Neo4j credentials (rule-based mode)
  - For live database analysis, verify your Neo4j credentials
  - Check that your Neo4j database is accessible from your machine

**5. Permission Issues**
- **Problem**: "Permission denied" errors
- **Solution**: 
  - Make the script executable: `chmod +x src/mcp_neo4j_optimizer/agent.py`
  - Check file permissions on the configuration file
  - Ensure you have read access to the project directory

### Testing Steps

1. **Test Python Environment**:
   ```bash
   python --version
   python -c "import neo4j, dotenv; print('Dependencies OK')"
   ```

2. **Test MCP Server**:
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python src/mcp_neo4j_optimizer/agent.py
   ```

3. **Test Configuration**:
   ```bash
   python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

### Getting Help

If you're still having issues:
1. Check the error messages in Claude Desktop logs
2. Test the MCP server directly using the commands above
3. Verify your configuration file syntax
4. Ensure all paths are correct and accessible

## 📚 Next Steps

1. **Read the README** for detailed usage information
2. **Check the API documentation** at `/docs` when running the web server
3. **Explore the supported operators** using the `get-optimization-status` tool
4. **Test with your own queries** to see optimization recommendations

## 🤝 Support

- **Issues**: Report bugs on GitHub
- **Documentation**: Check the README.md file
- **Examples**: See the `examples/` directory

---

**Happy Query Optimizing! 🚀** 