# Discovery Integration Workflow

## How to Use Component Discovery in Flow Building

### Discovery-First Workflow
```
1. User requests MCP functionality → 2. Run component_discovery → 3. Use results to configure MCP components → 4. Build flow
```

### Processing Discovery Results

**Success Response (`status: "success"`):**
1. Extract tools: `discovered_capabilities.available_tools`
2. Get schemas: `langflow_schemas[tool_name]` for each tool
3. Use recommendations: `recommendations.suggested_tools` and `component_config`
4. Configure MCP component with exact field types and requirements

**Failed Response (`status: "failed"`):**
- Check `errors` array for specific issues
- Inform user about connectivity problems
- Suggest alternative approaches or manual configuration

### Schema Application

**From Discovery Result:**
```json
"langflow_schemas": {
  "send_email": [
    {"name": "to", "type": "MessageTextInput", "required": true},
    {"name": "subject", "type": "MessageTextInput", "required": true},
    {"name": "priority", "type": "DropdownInput", "options": ["low", "normal", "high"]}
  ]
}
```

**To MCP Component Config:**
```python
# Use connection config from discovery recommendations
MCPNode(
    connection_type="http",                    # Infered from user inpu
    server_url="https://mcp.composio.dev/...", # Infered from user inpu
    tool_name="send_email",                   # from discovery
    to="{{ user_input.email }}",              # MessageTextInput
    subject="{{ user_input.subject }}",       # MessageTextInput
    priority="normal"                          # DropdownInput with default
)
```

### Integration Best Practices

- **Always discover before MCP configuration** - schemas vary by server
- **Use suggested tools first** - from `recommendations.suggested_tools`
- **Match requirements** - pass user requirements to get relevant tool recommendations
- **Handle connection errors gracefully** - provide clear user feedback when discovery fails