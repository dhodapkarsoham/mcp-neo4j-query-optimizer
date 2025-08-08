# Neo4j Query Optimizer MCP Agent - API Documentation

## Overview
This MCP (Model Context Protocol) agent provides comprehensive Neo4j query optimization and analysis capabilities.

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

**Output**: Comprehensive analysis including:
- Original query plan analysis
- Optimized query with suggestions
- Performance comparison
- Improvement recommendations

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

**Output**: Detailed performance analysis including:
- Query plan structure
- Performance issues identified
- Specific recommendations
- Impact explanations

## Performance Issue Severity Levels

### 🔴 Critical
- `AllNodesScan` - Full database scans
- `CartesianProduct` - Missing join conditions
- `DirectedAllRelationshipsScan` - Scanning all relationships

### 🟡 High  
- `NodeByLabelScan` - Label scans without indexes
- `NodeIndexScan` - Index scans instead of seeks
- `Expand` - Large relationship expansions
- High database hits (>10,000)

### 🟢 Medium
- `Filter` - Large filtering operations
- `Sort` - Large sorting operations  
- `Aggregate` - Large aggregations
- `Unwind` - Large array unwinding
- `Limit` - Large limit operations
- `Skip` - Large skip operations
- `NodeHashJoin` - Large hash joins
- `Apply` - Subquery execution

## Configuration
The agent requires Neo4j credentials to be configured in the Claude Desktop config:

```json
{
  "mcpServers": {
    "neo4j-optimizer-agent": {
      "command": "python",
      "args": ["path/to/neo4j_optimizer_agent.py"],
      "env": {
        "NEO4J_URI": "bolt+s://your-db-id.databases.neo4j.io",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

## Usage Examples

### Basic Query Analysis
```
"Can you analyze this query: MATCH (n) RETURN n"
```

### Query Optimization
```
"Can you optimize this query: MATCH (a)-[r]->(b) WHERE a.name = 'John' RETURN b"
```

### Performance Investigation
```
"What performance issues does this query have: MATCH (n:Person) WHERE n.age > 30 ORDER BY n.name RETURN n"
``` 