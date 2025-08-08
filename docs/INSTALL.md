# 🚀 Installation Guide for MCP Neo4j Query Optimizer

This guide will help you install and configure the MCP Neo4j Query Optimizer server for use with Claude Desktop and other MCP clients.

## 📋 Prerequisites

- Python 3.8 or higher
- Neo4j database (local or cloud)
- MCP client (Claude Desktop, etc.)

## 🔧 Installation Methods

### Method 1: Install from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/mcp-neo4j-query-optimizer.git
   cd mcp-neo4j-query-optimizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j connection details
   ```

### Method 2: Install via pip (when published)

```bash
pip install mcp-neo4j-query-optimizer
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file or set environment variables:

```bash
# Neo4j Connection
NEO4J_URI=bolt+s://your-db-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### 2. MCP Client Configuration

#### For Claude Desktop

1. Open Claude Desktop
2. Go to Settings → MCP
3. Add the server configuration:

```json
{
  "mcpServers": {
    "neo4j-query-optimizer": {
      "command": "mcp-neo4j-query-optimizer",
      "env": {
        "NEO4J_URI": "bolt+s://your-db-id.databases.neo4j.io",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

#### For Other MCP Clients

Use the configuration from `mcp-neo4j-query-optimizer.json` as a template.

## 🧪 Testing the Installation

### 1. Test the MCP Server Directly

```bash
# Test the server
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | mcp-neo4j-query-optimizer
```

### 2. Test with a Simple Query

```bash
# Test optimization
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "optimize-query", "arguments": {"query": "MATCH (n) RETURN n LIMIT 5"}}}' | mcp-neo4j-query-optimizer
```

## 🛠️ Available Tools

Once installed, you'll have access to these tools:

### 1. `optimize-query`
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
Analyze a query execution plan.

**Parameters:**
- `query` (required): The Cypher query
- `plan` (optional): Pre-existing query plan
- `database` (optional): Database name

### 3. `get-optimization-status`
Get server status and supported operators.

**Parameters:** None

### 4. `suggest-indexes`
Generate index suggestions for a query.

**Parameters:**
- `query` (required): The Cypher query
- `database` (optional): Database name

## 🔍 Usage Examples

### In Claude Desktop

1. **Optimize a query**:
   ```
   Can you optimize this Cypher query: MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10
   ```

2. **Get optimization status**:
   ```
   What operators does the query optimizer support?
   ```

3. **Suggest indexes**:
   ```
   Suggest indexes for: MATCH (p:Product)-[:HAS_SKU]->(s:SKU) WHERE p.category = 'Electronics' RETURN p, s
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