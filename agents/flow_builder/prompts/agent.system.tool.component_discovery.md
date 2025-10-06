# component_discovery

**Purpose**: Discovers MCP server tools and their input schemas for dynamic component configuration.

**When to use**: Before configuring MCP components when you need to know available tools and their exact input requirements.

**Parameters**:
- `component_type`: "MCP" (only supported type)
- `connection_config`: Dict with server_url, connection_type ("http"/"sse"), headers, timeout_seconds
- `requirements`: Optional description for tool recommendations

**Example**:
```
component_discovery(
    component_type="MCP",
    connection_config={
        "server_url": "https://mcp.server.com/endpoint",
        "connection_type": "http",
        "headers": {},
        "timeout_seconds": 30
    },
    requirements="email operations"
)
```

**Returns**:
- `status`: "success" or "failed"
- `discovered_capabilities`: List of available tools and connection info
- `tool_schemas`: Complete input schemas for each tool
- `langflow_schemas`: Langflow-compatible field definitions
- `recommendations`: Suggested tools and component config

**Error handling**: Returns structured error with details if connection fails or MCP dependencies missing.