# Neo4j Query Optimizer MCP Agent - API Documentation

## Overview
This MCP (Model Context Protocol) agent extracts structured operator data from Neo4j query plans and provides rich context for MCP clients to interpret and provide intelligent optimization recommendations.

## Architecture

The agent follows the proper MCP architecture pattern:
- **MCP Server**: Extracts structured operator data from Neo4j query plans
- **MCP Client**: Interprets data and provides intelligent recommendations using knowledge of Neo4j operators

## Available Tools

### 1. `optimize-neo4j-query`
**Description**: Analyze a Neo4j query, optimize it, and compare the before/after query plans to show improvements.

**Input Schema**:
```json
{
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
```

**Example Usage**:
```json
{
  "name": "optimize-neo4j-query",
  "arguments": {
    "query": "MATCH (n) RETURN n",
    "database": "neo4j"
  }
}
```

**Output**: Structured data including:
- **Structured operator data** with performance characteristics
- **Query metadata** and patterns
- **Performance indicators** for MCP client interpretation
- **Rich context** for intelligent recommendations
- **Before/after comparison** with optimization suggestions

### 2. `analyze-query-plan`
**Description**: Get detailed query plan analysis for a Cypher query without optimization.

**Input Schema**:
```json
{
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
```

**Example Usage**:
```json
{
  "name": "analyze-query-plan",
  "arguments": {
    "query": "MATCH (n:Person) WHERE n.age > 30 RETURN n",
    "database": "neo4j"
  }
}
```

**Output**: Structured data including:
- **Structured operator data** with performance characteristics
- **Query metadata** and patterns
- **Performance indicators** for MCP client interpretation
- **Rich context** for intelligent recommendations
- **Operator classification** based on official Neo4j documentation

## Structured Data Format

### Operator Data Structure
```json
{
  "operator": "NodeByLabelScan",
  "clean_operator": "NodeByLabelScan",
  "estimated_rows": 1000,
  "db_hits": 1000,
  "depth": 0,
  "args": {},
  "identifiers": ["n"],
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
```

### Performance Indicators
- `high_row_count` - Estimated rows > 100,000
- `high_db_hits` - Database hits > 10,000
- `full_scan` - AllNodesScan or UndirectedAllRelationshipsScan
- `cartesian_product` - CartesianProduct operator
- `index_usage` - Index-based operators
- `eager_operation` - Eager operators

### Operator Classification
Based on official [Neo4j operators documentation](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/):

**Leaf Operators**: AllNodesScan, NodeByLabelScan, NodeIndexSeek, etc.
**Updating Operators**: Create, Delete, SetProperties, etc.
**Eager Operators**: EagerAggregation, CartesianProduct, etc.

## Configuration
The agent works with or without Neo4j credentials:

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

## Usage Examples

### Basic Query Analysis
```
"Can you analyze this query using the neo4j-query-optimizer: MATCH (n) RETURN n"
```

### Query Optimization
```
"Can you optimize this query using the neo4j-query-optimizer: MATCH (a)-[r]->(b) WHERE a.name = 'John' RETURN b"
```

### Performance Investigation
```
"What performance issues does this query have using the neo4j-query-optimizer: MATCH (n:Person) WHERE n.age > 30 ORDER BY n.name RETURN n"
```

### Direct Tool Usage
```
@neo4j-query-optimizer analyze-query-plan "MATCH (n:Person) WHERE n.age > 30 RETURN n"
```

## MCP Client Integration

The MCP server provides structured data that MCP clients can interpret using their knowledge of Neo4j operators. The client can:

1. **Analyze Performance**: Interpret performance indicators and characteristics
2. **Provide Recommendations**: Generate optimization suggestions based on operator data
3. **Create Indexes**: Suggest specific index creation statements
4. **Explain Operators**: Provide educational content about Neo4j operators
5. **Compare Queries**: Generate before/after comparisons and explanations

Reference: [Neo4j Operators Documentation](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/) 