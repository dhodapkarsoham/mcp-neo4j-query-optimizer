# Neo4j Query Optimizer - Structured Data Examples

This document provides comprehensive examples of the structured data output from the Neo4j Query Optimizer MCP server.

## Overview

The MCP server extracts structured operator data from Neo4j query plans and provides rich context for MCP clients to interpret and provide intelligent optimization recommendations.

## Example 1: Simple Node Scan

### Input Query
```cypher
MATCH (n) RETURN n LIMIT 10
```

### Structured Data Output
```json
{
  "query": "MATCH (n) RETURN n LIMIT 10",
  "query_type": "read",
  "complexity": "low",
  "query_patterns": ["node matching", "result limiting"],
  "operators": [
    {
      "operator": "AllNodesScan",
      "clean_operator": "AllNodesScan",
      "estimated_rows": 100000,
      "db_hits": 100000,
      "depth": 0,
      "args": {},
      "identifiers": ["n"],
      "is_leaf": true,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "AllNodesScan",
        "estimated_rows": 100000,
        "db_hits": 100000,
        "performance_indicators": ["full_scan", "high_row_count"]
      }
    },
    {
      "operator": "Limit",
      "clean_operator": "Limit",
      "estimated_rows": 10,
      "db_hits": 0,
      "depth": 1,
      "args": {"rows": 10},
      "identifiers": ["n"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Limit",
        "estimated_rows": 10,
        "db_hits": 0,
        "performance_indicators": []
      }
    }
  ],
  "summary": {
    "total_operators": 2,
    "leaf_operators": 1,
    "updating_operators": 0,
    "eager_operators": 0,
    "estimated_total_rows": 100000,
    "estimated_db_hits": 100000
  },
  "performance_indicators": ["full_scan", "high_row_count"],
  "query_metadata": {
    "has_where_clause": false,
    "has_order_by": false,
    "has_limit": true,
    "has_aggregation": false,
    "has_relationships": false
  }
}
```

### MCP Client Interpretation
Based on this structured data, the MCP client can provide:
- **Performance Analysis**: Full database scan with high row count indicates critical performance issues
- **Optimization Suggestions**: Add labels to MATCH clause (e.g., `MATCH (n:Person)`)
- **Index Recommendations**: Create indexes on frequently queried properties
- **Best Practices**: Always use labels in MATCH clauses to avoid full scans

## Example 2: Labeled Node with Filter

### Input Query
```cypher
MATCH (n:Person) WHERE n.age > 30 RETURN n.name ORDER BY n.name LIMIT 100
```

### Structured Data Output
```json
{
  "query": "MATCH (n:Person) WHERE n.age > 30 RETURN n.name ORDER BY n.name LIMIT 100",
  "query_type": "read",
  "complexity": "medium",
  "query_patterns": ["node matching", "property filtering", "result sorting", "result limiting"],
  "operators": [
    {
      "operator": "NodeByLabelScan",
      "clean_operator": "NodeByLabelScan",
      "estimated_rows": 50000,
      "db_hits": 50000,
      "depth": 0,
      "args": {"labelName": "Person"},
      "identifiers": ["n"],
      "is_leaf": true,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "NodeByLabelScan",
        "estimated_rows": 50000,
        "db_hits": 50000,
        "performance_indicators": ["high_row_count"]
      }
    },
    {
      "operator": "Filter",
      "clean_operator": "Filter",
      "estimated_rows": 15000,
      "db_hits": 0,
      "depth": 1,
      "args": {"predicate": "n.age > 30"},
      "identifiers": ["n"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Filter",
        "estimated_rows": 15000,
        "db_hits": 0,
        "performance_indicators": []
      }
    },
    {
      "operator": "Sort",
      "clean_operator": "Sort",
      "estimated_rows": 15000,
      "db_hits": 0,
      "depth": 2,
      "args": {"sortItems": ["n.name"]},
      "identifiers": ["n"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Sort",
        "estimated_rows": 15000,
        "db_hits": 0,
        "performance_indicators": []
      }
    },
    {
      "operator": "Limit",
      "clean_operator": "Limit",
      "estimated_rows": 100,
      "db_hits": 0,
      "depth": 3,
      "args": {"rows": 100},
      "identifiers": ["n"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Limit",
        "estimated_rows": 100,
        "db_hits": 0,
        "performance_indicators": []
      }
    }
  ],
  "summary": {
    "total_operators": 4,
    "leaf_operators": 1,
    "updating_operators": 0,
    "eager_operators": 0,
    "estimated_total_rows": 50000,
    "estimated_db_hits": 50000
  },
  "performance_indicators": ["high_row_count"],
  "query_metadata": {
    "has_where_clause": true,
    "has_order_by": true,
    "has_limit": true,
    "has_aggregation": false,
    "has_relationships": false
  }
}
```

### MCP Client Interpretation
Based on this structured data, the MCP client can provide:
- **Performance Analysis**: High row count in NodeByLabelScan indicates potential performance issues
- **Optimization Suggestions**: Create indexes on `age` and `name` properties
- **Index Recommendations**: 
  - `CREATE INDEX FOR (n:Person) ON (n.age)`
  - `CREATE INDEX FOR (n:Person) ON (n.name)`
- **Best Practices**: Use composite indexes for filtered and sorted properties

## Example 3: Relationship Traversal

### Input Query
```cypher
MATCH (p:Person)-[:KNOWS]->(f:Person) WHERE p.age > 25 RETURN p.name, f.name LIMIT 50
```

### Structured Data Output
```json
{
  "query": "MATCH (p:Person)-[:KNOWS]->(f:Person) WHERE p.age > 25 RETURN p.name, f.name LIMIT 50",
  "query_type": "read",
  "complexity": "medium",
  "query_patterns": ["node matching", "relationship traversal", "property filtering", "result limiting"],
  "operators": [
    {
      "operator": "NodeByLabelScan",
      "clean_operator": "NodeByLabelScan",
      "estimated_rows": 50000,
      "db_hits": 50000,
      "depth": 0,
      "args": {"labelName": "Person"},
      "identifiers": ["p"],
      "is_leaf": true,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "NodeByLabelScan",
        "estimated_rows": 50000,
        "db_hits": 50000,
        "performance_indicators": ["high_row_count"]
      }
    },
    {
      "operator": "Filter",
      "clean_operator": "Filter",
      "estimated_rows": 20000,
      "db_hits": 0,
      "depth": 1,
      "args": {"predicate": "p.age > 25"},
      "identifiers": ["p"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Filter",
        "estimated_rows": 20000,
        "db_hits": 0,
        "performance_indicators": []
      }
    },
    {
      "operator": "Expand(All)",
      "clean_operator": "Expand(All)",
      "estimated_rows": 100000,
      "db_hits": 100000,
      "depth": 2,
      "args": {"relationshipType": "KNOWS", "direction": "outgoing"},
      "identifiers": ["p", "f"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Expand(All)",
        "estimated_rows": 100000,
        "db_hits": 100000,
        "performance_indicators": ["high_row_count", "high_db_hits"]
      }
    },
    {
      "operator": "Limit",
      "clean_operator": "Limit",
      "estimated_rows": 50,
      "db_hits": 0,
      "depth": 3,
      "args": {"rows": 50},
      "identifiers": ["p", "f"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Limit",
        "estimated_rows": 50,
        "db_hits": 0,
        "performance_indicators": []
      }
    }
  ],
  "summary": {
    "total_operators": 4,
    "leaf_operators": 1,
    "updating_operators": 0,
    "eager_operators": 0,
    "estimated_total_rows": 100000,
    "estimated_db_hits": 150000
  },
  "performance_indicators": ["high_row_count", "high_db_hits"],
  "query_metadata": {
    "has_where_clause": true,
    "has_order_by": false,
    "has_limit": true,
    "has_aggregation": false,
    "has_relationships": true
  }
}
```

### MCP Client Interpretation
Based on this structured data, the MCP client can provide:
- **Performance Analysis**: High row count and DB hits indicate expensive relationship traversal
- **Optimization Suggestions**: 
  - Create indexes on `age` property
  - Consider using relationship indexes
  - Add LIMIT earlier in the query
- **Index Recommendations**: 
  - `CREATE INDEX FOR (n:Person) ON (n.age)`
  - `CREATE INDEX FOR ()-[r:KNOWS]-() ON (r)`
- **Best Practices**: Use relationship type filters and consider query structure

## Example 4: Aggregation Query

### Input Query
```cypher
MATCH (p:Person) WHERE p.department = 'Engineering' RETURN p.department, COUNT(p) as employee_count
```

### Structured Data Output
```json
{
  "query": "MATCH (p:Person) WHERE p.department = 'Engineering' RETURN p.department, COUNT(p) as employee_count",
  "query_type": "read",
  "complexity": "medium",
  "query_patterns": ["node matching", "property filtering", "aggregation"],
  "operators": [
    {
      "operator": "NodeByLabelScan",
      "clean_operator": "NodeByLabelScan",
      "estimated_rows": 50000,
      "db_hits": 50000,
      "depth": 0,
      "args": {"labelName": "Person"},
      "identifiers": ["p"],
      "is_leaf": true,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "NodeByLabelScan",
        "estimated_rows": 50000,
        "db_hits": 50000,
        "performance_indicators": ["high_row_count"]
      }
    },
    {
      "operator": "Filter",
      "clean_operator": "Filter",
      "estimated_rows": 5000,
      "db_hits": 0,
      "depth": 1,
      "args": {"predicate": "p.department = 'Engineering'"},
      "identifiers": ["p"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": false,
      "performance_characteristics": {
        "operator_type": "Filter",
        "estimated_rows": 5000,
        "db_hits": 0,
        "performance_indicators": []
      }
    },
    {
      "operator": "EagerAggregation",
      "clean_operator": "EagerAggregation",
      "estimated_rows": 1,
      "db_hits": 0,
      "depth": 2,
      "args": {"groupingKeys": ["p.department"], "aggregatingExpressions": ["COUNT(p)"]},
      "identifiers": ["p"],
      "is_leaf": false,
      "is_updating": false,
      "is_eager": true,
      "performance_characteristics": {
        "operator_type": "EagerAggregation",
        "estimated_rows": 1,
        "db_hits": 0,
        "performance_indicators": ["eager_operation"]
      }
    }
  ],
  "summary": {
    "total_operators": 3,
    "leaf_operators": 1,
    "updating_operators": 0,
    "eager_operators": 1,
    "estimated_total_rows": 50000,
    "estimated_db_hits": 50000
  },
  "performance_indicators": ["high_row_count", "eager_operation"],
  "query_metadata": {
    "has_where_clause": true,
    "has_order_by": false,
    "has_limit": false,
    "has_aggregation": true,
    "has_relationships": false
  }
}
```

### MCP Client Interpretation
Based on this structured data, the MCP client can provide:
- **Performance Analysis**: High row count with eager aggregation indicates memory-intensive operation
- **Optimization Suggestions**: 
  - Create index on `department` property
  - Consider using `COUNT(*)` instead of `COUNT(p)`
  - Add LIMIT if appropriate
- **Index Recommendations**: `CREATE INDEX FOR (n:Person) ON (n.department)`
- **Best Practices**: Use indexes on filtered properties, consider aggregation performance

## Performance Indicators Reference

### High-Level Indicators
- `high_row_count` - Estimated rows > 100,000
- `high_db_hits` - Database hits > 10,000
- `full_scan` - AllNodesScan or UndirectedAllRelationshipsScan
- `cartesian_product` - CartesianProduct operator
- `index_usage` - Index-based operators
- `eager_operation` - Eager operators

### Operator Types
- **Leaf Operators**: AllNodesScan, NodeByLabelScan, NodeIndexSeek, etc.
- **Updating Operators**: Create, Delete, SetProperties, etc.
- **Eager Operators**: EagerAggregation, CartesianProduct, etc.

## MCP Client Integration

The structured data provided by the MCP server enables MCP clients to:

1. **Analyze Performance**: Interpret performance indicators and characteristics
2. **Provide Recommendations**: Generate optimization suggestions based on operator data
3. **Create Indexes**: Suggest specific index creation statements
4. **Explain Operators**: Provide educational content about Neo4j operators
5. **Compare Queries**: Generate before/after comparisons and explanations

Reference: [Neo4j Operators Documentation](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/)
