# langflow_publisher

**Purpose**: Imports flow JSON files to Langflow instance with automatic timestamping.

**When to use**: After building a flow with flow_builder, use this to upload it to your Langflow instance.

**Parameters**:
- `flow_json_file`: Path to the JSON flow file (required)
- `langflow_url`: Langflow URL (optional, defaults to LANGFLOW_URL env var or http://localhost:7860)
- `api_key`: API key (optional, defaults to LANGFLOW_API_KEY env var)

**Features**:
- Uploads flow JSON files directly to Langflow with proper Unicode support
- Uses Langflow's upload API endpoint
- Supports environment variable configuration
- Handles UTF-8 encoded JSON files correctly (no encoding fixes needed)

**Returns**: Success message with flow name or error details

**Example**:
```json
{
    "tool_name": "langflow_publisher",
    "tool_args": {
        "flow_json_file": "/a0/flow_builder/flows/chat_agent.json",
        "langflow_url": "http://localhost:7860",
        "api_key": "your-api-key"
    }
}
```