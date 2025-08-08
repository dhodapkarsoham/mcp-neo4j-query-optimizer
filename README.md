# 🔍 Neo4j Query Optimizer MCP Agent

A comprehensive MCP (Model Context Protocol) server for analyzing and optimizing Neo4j Cypher queries using intelligent operator-based analysis. Perfect for integration with Claude Desktop and other MCP clients.

## ✨ Features

- **🔍 Query Plan Analysis**: Analyzes Neo4j query execution plans
- **🚨 Performance Issue Detection**: Identifies critical, high, medium, and low severity issues
- **💡 Smart Recommendations**: Provides specific, actionable optimization advice
- **📚 Index Suggestions**: Generates exact CREATE INDEX statements
- **✏️ Query Rewrites**: Shows before/after query examples
- **⚡ MCP Integration**: Works seamlessly with Claude Desktop and other MCP clients
- **📊 Detailed Analytics**: Comprehensive analysis with severity levels and impact assessment

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

## 🔧 Supported Operators

The optimizer analyzes these Neo4j query plan operators:

| Operator | Severity | Description |
|----------|----------|-------------|
| **AllNodesScan** | Critical | Full database scan |
| **NodeByLabelScan** | High | Label-based scan |
| **NodeIndexScan** | Low | Index usage (good) |
| **CartesianProduct** | Critical | Cross-join operation |
| **Expand** | Medium | Relationship expansion |
| **Filter** | Medium | Late-applied filters |
| **Sort** | Medium | Sorting operations |
| **Limit** | Low | Result limiting (good) |
| **Skip** | Medium | Pagination operations |
| **Aggregation** | Medium | Data aggregation |
| **DirectedAllRelationshipsScan** | High | Relationship scans |
| **UndirectedAllRelationshipsScan** | Critical | Bidirectional scans |

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
│   Claude        │    │   MCP Agent      │    │   Neo4j         │
│   Desktop       │◄──►│   (JSON-RPC)     │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Query Optimizer  │
                       │ (Operator-based) │
                       └──────────────────┘
```

## 🔍 Example Analysis

**Input Query**:
```cypher
MATCH (n) WHERE n.name = 'test' RETURN n LIMIT 10
```

**Analysis Results**:
```json
{
  "performance_issues": [
    "Full database scan - very expensive operation (Severity: Critical)",
    "Filter applied after data retrieval (Severity: Medium)",
    "Limiting results - this is good (Severity: Low)"
  ],
  "recommendations": [
    "Create indexes on frequently queried properties (Priority: Critical)",
    "Move filter conditions earlier in the query (Priority: Medium)"
  ],
  "index_suggestions": [
    "CREATE INDEX FOR (n:Label) ON (n.property)"
  ],
  "query_rewrites": [
    "MATCH (n) WHERE n.property = value → MATCH (n:Label {property: value})"
  ]
}
```

## 🛠️ MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `optimize-neo4j-query` | Complete optimization workflow | `query` (required), `database` (optional) |
| `analyze-query-plan` | Single query plan analysis | `query` (required), `database` (optional) |

## 🎨 MCP Agent Features

- **Real Database Analysis**: Connects to your actual Neo4j database
- **Comprehensive Operator Coverage**: Analyzes 15+ Neo4j query plan operators
- **Before/After Comparison**: Shows exact performance improvements
- **Actionable Recommendations**: Specific index suggestions and query rewrites
- **Severity-based Analysis**: Critical, High, Medium, and Low priority issues
- **Claude Integration**: Works seamlessly with Claude Desktop

## 🔧 Configuration

### MCP Client Configuration

Add this to your Claude Desktop or other MCP client configuration:

```json
{
  "mcpServers": {
    "neo4j-optimizer-agent": {
      "command": "python",
      "args": ["/path/to/your/src/mcp_neo4j_optimizer/agent.py"],
      "env": {
        "NEO4J_URI": "bolt+s://your-db-id.databases.neo4j.io",
        "NEO4J_USER": "neo4j", 
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEO4J_URI` | Neo4j database URI | Yes |
| `NEO4J_USER` | Neo4j username | Yes |
| `NEO4J_PASSWORD` | Neo4j password | Yes |

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

---

**Happy Query Optimizing! 🚀** 