# 🔍 Neo4j Query Optimizer MCP Server

[![PyPI version](https://badge.fury.io/py/mcp-neo4j-query-optimizer.svg)](https://badge.fury.io/py/mcp-neo4j-query-optimizer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-green.svg)](https://neo4j.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io/)

> **⚠️ Work in Progress**: This repository is actively being developed. Feel free to try it out and provide feedback, but expect some changes and improvements as we development continues.

A comprehensive MCP (Model Context Protocol) server that extracts structured operator data from Neo4j query plans and provides rich context for MCP clients to interpret and provide intelligent optimization recommendations. Perfect for integration with Claude Desktop and other MCP clients.

## ✨ Features

- **🔍 Structured Data Extraction**: Extracts comprehensive operator data from Neo4j query plans
- **📊 Performance Analysis**: Identifies performance indicators and characteristics
- **🎯 Operator Classification**: Based on official [Neo4j operators documentation](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/)
- **🧠 MCP Client Intelligence**: Provides rich context for intelligent recommendations
- **⚡ Query Optimization**: Basic optimization with before/after comparisons
- **🧪 Comprehensive Testing**: 38 unit tests ensuring reliability
- **🔗 Universal Compatibility**: Works with any MCP client (Claude Desktop, etc.)
- **📈 Rich Context**: Structured data for intelligent conversations
- **🚀 Fast & Reliable**: No external API dependencies, works offline

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Neo4j database (local or cloud)
- Claude Desktop or other MCP client

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp-query-optimizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Configure Neo4j connection**:
   Set up your Neo4j credentials in your MCP client configuration (see Configuration section below)

4. **Configure MCP client**:
   Add the server to your Claude Desktop or other MCP client configuration

## 🎯 Usage

### Available Tools

The MCP server provides two main tools:

1. **`optimize-neo4j-query`**: Full optimization workflow with before/after comparison and rich context for conversations
2. **`analyze-query-plan`**: Single query plan analysis with rich context for discussions

### Claude Desktop Integration

1. **Configure the MCP server** in Claude Desktop settings
2. **Ask Claude to optimize queries**:
   ```
   Can you optimize this Cypher query: MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10
   ```
3. **Get detailed analysis**:
   ```
   What performance issues does this query have: MATCH (p:Product)-[:HAS_SKU]->(s:SKU) WHERE p.category = 'Electronics' RETURN p, s
   ```

### Direct MCP Usage

#### Test the server directly:
```bash
# List available tools
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python src/mcp_neo4j_optimizer/agent.py

# Optimize a query
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "optimize-neo4j-query", "arguments": {"query": "MATCH (n) RETURN n"}}}' | python src/mcp_neo4j_optimizer/agent.py
```

## 📊 Analysis Output

The optimizer provides:

### Performance Issues
- **Critical**: Full database scans, Cartesian products
- **High**: Missing indexes, inefficient scans
- **Medium**: Late filters, sorting issues
- **Low**: Well-optimized operations

### Recommendations
- Specific optimization strategies
- Implementation guidance
- Priority-based suggestions

### Index Suggestions
- Exact CREATE INDEX statements
- Property-specific recommendations
- Composite index suggestions

### Query Rewrites
- Before/after query examples
- Improved query structures
- Performance-focused alternatives

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Server     │    │   Neo4j         │
│ (Claude, etc.)  │◄──►│                  │◄──►│   Database      │
│                 │    │                  │    │                 │
│ • Interprets    │    │ • Extracts       │    │ • Query Plans   │
│   operators     │    │   operator data  │    │ • Execution     │
│ • Provides      │    │ • Classifies     │    │   Stats         │
│   recommendations│    │   operators      │    │                 │
│ • Generates     │    │ • Structures     │    │                 │
│   optimizations │    │   data           │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🎯 **Proper MCP Architecture**

**MCP Server Responsibilities:**
- Extracts structured operator data from Neo4j query plans
- Classifies operators based on official Neo4j documentation
- Provides performance indicators and characteristics
- Structures data for MCP client interpretation

**MCP Client Responsibilities:**
- Interprets operator data using knowledge of Neo4j operators
- Provides intelligent recommendations and optimizations
- Generates educational content and best practices
- Creates before/after comparisons and explanations

## 🔄 Recent Refactoring (v2.0) - Proper MCP Architecture

**Major Changes:**
- ✅ **Structured Data Extraction**: MCP server extracts operator data, client provides intelligence
- ✅ **Operator Classification**: Based on [Neo4j operators documentation](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/)
- ✅ **Comprehensive Testing**: Added 38 unit tests covering all functionality

**Proper MCP Architecture:**
- 🎯 **MCP Server**: Extracts structured operator data from Neo4j query plans
- 🧠 **MCP Client**: Uses knowledge of Neo4j operators to provide intelligent recommendations
- 📊 **Structured Data**: Rich context with operator details, performance indicators, and metadata
- 🔗 **Official Reference**: Links to Neo4j documentation for operator understanding

## 🔍 Example Analysis

**Input Query**:
```cypher
MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10
```

**Structured Data Output**:
```json
{
  "query": "MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10",
  "query_type": "read",
  "complexity": "medium",
  "query_patterns": ["node matching", "property filtering", "result limiting"],
  "operators": [
    {
      "operator": "NodeByLabelScan",
      "clean_operator": "NodeByLabelScan",
      "estimated_rows": 1000,
      "db_hits": 1000,
      "is_leaf": true,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "NodeByLabelScan",
        "estimated_rows": 1000,
        "db_hits": 1000,
        "performance_indicators": ["high_row_count"]
      }
    }
  ],
  "summary": {
    "total_operators": 3,
    "leaf_operators": 1,
    "updating_operators": 0,
    "eager_operators": 0,
    "estimated_total_rows": 1000,
    "estimated_db_hits": 1000
  },
  "performance_indicators": ["high_row_count"],
  "query_metadata": {
    "has_where_clause": true,
    "has_order_by": false,
    "has_limit": true,
    "has_aggregation": false,
    "has_relationships": false
  }
}
```

**MCP Client Interpretation**:
Based on this structured data, the MCP client can provide:
- **Performance Analysis**: High row count indicates potential performance issues
- **Optimization Suggestions**: Create indexes on filtered properties
- **Index Recommendations**: `CREATE INDEX FOR (n:Node) ON (n.name)`
- **Best Practices**: Use labels in MATCH clauses for better performance

## 🛠️ MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `optimize-neo4j-query` | Analyze and optimize a Neo4j query with before/after comparison | `query` (required), `database` (optional) |
| `analyze-query-plan` | Get detailed structured analysis of a query execution plan | `query` (required), `database` (optional) |

### 📋 **Tool Outputs**

Both tools provide:
- **Structured operator data** with performance characteristics
- **Query metadata** and patterns
- **Performance indicators** for MCP client interpretation
- **Rich context** for intelligent recommendations
- **References** to official Neo4j documentation

## 🎨 MCP Agent Features

- **Structured Data Extraction**: Extracts comprehensive operator data from Neo4j query plans
- **Operator Classification**: Based on official [Neo4j operators documentation](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/)
- **Performance Analysis**: Identifies performance indicators and characteristics
- **Rich Context Generation**: Provides structured data for MCP client interpretation
- **Universal Compatibility**: Works with any MCP client (Claude Desktop, etc.)
- **Offline Operation**: No external API dependencies, works completely offline

## 🔧 Configuration

### MCP Client Configuration

Add this to your Claude Desktop or other MCP client configuration:

**For Claude Desktop** (macOS):
```json
{
  "mcpServers": {
    "neo4j-query-optimizer": {
      "command": "python",
      "args": ["/path/to/your/mcp-query-optimizer/src/mcp_neo4j_optimizer/agent.py"],
      "env": {
        "NEO4J_URI": "neo4j+s://your-db-id.databases.neo4j.io",
        "NEO4J_USER": "neo4j", 
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

**Configuration File Location**:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Important Notes**:
- Replace the Python path with your actual Python executable path
- Replace the project path with your actual project location

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEO4J_URI` | Neo4j database URI | No* | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | No* | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | No* | `password` |

*Required for live database analysis. The MCP server works in rule-based analysis mode without these credentials.

## 🔧 Troubleshooting

### Common Issues

**1. MCP Server Not Loading**
- Check that the Python path in your configuration is correct
- Ensure the script path points to the actual `agent.py` file
- Verify the script is executable: `chmod +x src/mcp_neo4j_optimizer/agent.py`

**2. "No tools available" Error**
- Restart Claude Desktop completely after configuration changes
- Check the configuration file syntax with a JSON validator
- Ensure the MCP server name matches in your configuration

**3. Neo4j Connection Issues**
- The MCP server works without Neo4j credentials (rule-based mode)
- For live database analysis, verify your Neo4j credentials
- Check that your Neo4j database is accessible from your machine

**4. Python Dependencies**
- Install required dependencies: `pip install neo4j python-dotenv`
- Ensure you're using the correct Python environment

### Testing the MCP Server

Test the MCP server directly:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python src/mcp_neo4j_optimizer/agent.py
```

You should see a JSON response with available tools.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤖 Neo4j Query Optimizer Agent - MCP Server

This project provides an **intelligent Neo4j query optimization agent** that can be integrated directly into **Claude Desktop**! The agent analyzes your Cypher queries, generates optimized versions, and compares the execution plans to show you exactly how performance improves.

### Quick Setup for Claude Desktop

1. **Copy the configuration**:
   ```json
   {
     "mcpServers": {
       "neo4j-optimizer-agent": {
         "command": "/path/to/your/anaconda3/bin/python",
         "args": ["/path/to/your/neo4j_optimizer_agent.py"]
       }
     }
   }
   ```

2. **Add to Claude Desktop MCP settings**

3. **Use in Claude**:
   - "Can you optimize this Cypher query: `MATCH (n) RETURN n LIMIT 5`"
   - "Analyze the query plan for: `MATCH (p:Product)-[:HAS_SKU]->(s:SKU) WHERE p.category = 'Electronics' RETURN p, s`"
   - "Compare the before and after performance of my query optimization"

## 🎯 **What the Agent Does**

### **Core Functionality:**
1. **📊 Analyzes Original Query**: Gets the execution plan from your Neo4j database
2. **⚡ Generates Optimized Version**: Creates an improved query based on detected issues
3. **📈 Compares Plans**: Shows you exactly what improved and why
4. **💡 Provides Insights**: Explains the performance differences and next steps

### **Available MCP Tools**

- **`optimize-neo4j-query`**: Complete optimization workflow - analyzes original query, creates optimized version, compares execution plans
- **`analyze-query-plan`**: Deep dive into a single query's execution plan without optimization

### **Testing the Agent**

```bash
# Test tools list
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python neo4j_optimizer_agent.py

# Test query optimization
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "optimize-neo4j-query", "arguments": {"query": "MATCH (n) RETURN n"}}}' | python neo4j_optimizer_agent.py
```

## 🚀 **Agent Features**

- **🔍 Real Query Plan Analysis**: Connects to your actual Neo4j database
- **⚡ Smart Optimizations**: Detects AllNodesScan, CartesianProduct, and other expensive operations
- **📊 Before/After Comparison**: Shows operator changes, row estimates, and improvements
- **💡 Actionable Insights**: Suggests indexes, query rewrites, and performance tips
- **🎯 Production Ready**: Uses your actual database for realistic analysis

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub issues
- **Documentation**: Check `docs/API_DOCS.md` for detailed API documentation  
- **MCP Integration**: Use directly in Claude Desktop with the MCP server
- **Testing**: Test the server directly with the provided examples

## 📋 Troubleshooting

### Common Issues

**❌ "Neo4j credentials not found"**
- Ensure environment variables are set correctly
- Check your MCP client configuration

**❌ "Cannot resolve address"**
- Verify your Neo4j database is running
- Check your database credentials

**❌ "Connection timeout"**
- Check your network connection
- Verify Neo4j database is accessible

---

**Happy Query Optimizing! 🚀** 
