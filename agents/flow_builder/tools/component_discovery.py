import json
import sys
import os
from typing import Dict, List, Any, Optional, Union
from python.helpers.tool import Tool, Response
from python.helpers.files import get_abs_path

class ComponentDiscovery(Tool):
    """
    Discovery tool that simulates dynamic components to extract their schemas and capabilities.
    Uses component simulation approach - instantiates components and runs their discovery logic.
    """

    async def execute(self, component_type: str, connection_config: Dict[str, Any], requirements: str = "") -> Response:
        """
        Discover dynamic component capabilities by simulating the component.

        **Parameters**:
        - component_type: str
          The type of component to discover ("MCP", "API", etc.)
        - connection_config: dict
          Connection configuration (server_url, connection_type, headers, etc.)
        - requirements: str (optional)
          Description of what the component needs to do in the flow

        **Returns**:
        - JSON response with discovered tools, schemas, and recommendations
        """
        try:
            # Perform discovery directly
            if component_type.upper() == "MCP":
                result = await self._discover_mcp_component(connection_config, requirements)
            else:
                result = self._create_error_result(component_type, f"Unknown component type: {component_type}")

            # Ensure result is JSON serializable
            try:
                serialized_result = json.dumps(result, indent=2)
            except (TypeError, ValueError) as json_error:
                # If serialization fails, create a simpler error result
                error_result = self._create_error_result(component_type, f"JSON serialization failed: {str(json_error)}")
                serialized_result = json.dumps(error_result, indent=2)

            return Response(
                message=serialized_result,
                break_loop=False
            )

        except Exception as e:
            error_result = self._create_error_result(component_type, f"Discovery failed: {str(e)}")
            return Response(
                message=json.dumps(error_result, indent=2),
                break_loop=False
            )

    async def _discover_mcp_component(self, connection_config: Dict[str, Any], requirements: str) -> Dict[str, Any]:
        """
        Discover MCP component by simulating MCPNodeComponent.
        This is the core component simulation logic.
        """
        try:
            # Import MCPNodeClient directly to avoid langflow dependencies
            new_components_path = get_abs_path("new_components")
            if new_components_path not in sys.path:
                sys.path.insert(0, new_components_path)

            try:
                from mcp_node import MCPNodeClient
            except ImportError as import_error:
                return self._create_error_result("MCP", f"Failed to import MCPNodeClient: {str(import_error)}. Please ensure MCP dependencies are installed.")

            # Create temporary MCP client instance (avoiding full component)
            temp_client = MCPNodeClient()

            connection_type = connection_config.get("connection_type", "http")
            server_url = connection_config.get("server_url", "")
            headers = connection_config.get("headers", {})
            timeout_seconds = connection_config.get("timeout_seconds", 30)

            # Ensure headers is a dictionary and doesn't contain lists
            if not isinstance(headers, dict):
                headers = {}

            # Convert any list values in headers to strings to avoid hashing issues
            safe_headers = {}
            for key, value in headers.items():
                if isinstance(value, list):
                    safe_headers[key] = ', '.join(str(v) for v in value)
                else:
                    safe_headers[key] = value
            headers = safe_headers

            if not server_url:
                return self._create_error_result("MCP", "server_url is required")

            # Connect and get tools directly from client
            if connection_type == "http":
                tools = await temp_client.connect_http(server_url, headers, timeout_seconds)
            elif connection_type == "sse":
                tools = await temp_client.connect_sse(server_url, headers, timeout_seconds)
            else:
                return self._create_error_result("MCP", f"Unsupported connection type: {connection_type}")

            # Extract detailed schemas for each tool
            discovered_tools = {}
            langflow_schemas = {}

            for tool in tools:
                try:
                    if not hasattr(tool, 'name'):
                        continue

                    tool_name = tool.name
                    input_schema = getattr(tool, 'inputSchema', {})

                    # Simplified schema conversion without langflow dependencies
                    field_definitions = self._convert_schema_to_fields(input_schema)

                    discovered_tools[tool_name] = {
                        "description": getattr(tool, 'description', ''),
                        "input_schema": input_schema,
                        "langflow_fields": field_definitions
                    }

                    langflow_schemas[tool_name] = field_definitions
                except Exception as tool_error:
                    # Skip problematic tools but continue processing
                    continue

            # Create success result
            try:
                integration_notes = self._generate_integration_notes(discovered_tools, requirements)
            except Exception as notes_error:
                integration_notes = [f"Failed to generate integration notes: {str(notes_error)}"]

            result = {
                "status": "success",
                "component_type": "MCPNode",
                "connection_config": connection_config,
                "discovered_capabilities": {
                    "available_tools": list(discovered_tools.keys()),
                    "tool_count": len(discovered_tools),
                    "connection_successful": True,
                    "server_info": {
                        "url": server_url,
                        "connection_type": connection_type,
                        "session_id": getattr(temp_client, 'session_id', None) if hasattr(temp_client, 'session_id') else None
                    }
                },
                "tool_schemas": discovered_tools,
                "langflow_schemas": langflow_schemas,
                "recommendations": {
                    "suggested_tools": list(discovered_tools.keys())[:3],  # First 3 tools as suggestions
                    "component_config": {
                        "connection_type": connection_type,
                        "server_url": server_url,
                        "headers": headers,
                        "timeout_seconds": timeout_seconds
                    },
                    "integration_notes": integration_notes
                },
                "errors": []
            }

            # Clean up client to prevent async context errors
            try:
                if hasattr(temp_client, 'exit_stack'):
                    await temp_client.exit_stack.aclose()
            except Exception:
                pass  # Ignore cleanup errors

            return result

        except Exception as e:
            error_msg = f"MCP discovery failed: {str(e)}"
            return self._create_error_result("MCP", error_msg)

    def _convert_schema_to_fields(self, input_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert JSON schema to simplified field definitions without langflow dependencies.
        This replaces the complex langflow schema conversion with a simpler approach.
        """
        field_definitions = []

        # Handle schema structure
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])

        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type", "string")
            field_description = field_schema.get("description", "")
            field_enum = field_schema.get("enum", [])
            field_default = field_schema.get("default")

            # Map JSON schema types to Langflow input types
            langflow_type = self._map_json_type_to_langflow(field_type, field_enum)

            field_def = {
                "name": field_name,
                "display_name": field_name.replace("_", " ").title(),
                "type": langflow_type,
                "required": field_name in required,
                "description": field_description,
                "default_value": field_default,
            }

            # Add options for enum fields
            if field_enum:
                field_def["options"] = field_enum

            field_definitions.append(field_def)

        return field_definitions

    def _map_json_type_to_langflow(self, json_type: str, enum_values: List[str] = None) -> str:
        """Map JSON schema types to Langflow input types."""
        if enum_values:
            return "DropdownInput"

        type_mapping = {
            "string": "MessageTextInput",
            "integer": "IntInput",
            "number": "FloatInput",
            "boolean": "BoolInput",
            "array": "MultilineInput",
            "object": "DictInput"
        }

        return type_mapping.get(json_type, "MessageTextInput")

    def _generate_integration_notes(self, discovered_tools: Dict[str, Any], requirements: str) -> List[str]:
        """Generate helpful integration notes based on discovered tools and requirements."""
        notes = []

        if not discovered_tools:
            notes.append("No tools discovered - check server URL and connectivity")
            return notes

        tool_names = list(discovered_tools.keys())
        notes.append(f"Discovered {len(tool_names)} tools: {', '.join(tool_names)}")

        # Analyze requirements and suggest relevant tools
        if requirements:
            req_lower = requirements.lower()
            relevant_tools = []

            for tool_name in tool_names:
                tool_lower = tool_name.lower()
                if any(word in tool_lower for word in ["search", "query", "find"]) and "search" in req_lower:
                    relevant_tools.append(tool_name)
                elif any(word in tool_lower for word in ["file", "read", "write"]) and "file" in req_lower:
                    relevant_tools.append(tool_name)
                elif any(word in tool_lower for word in ["web", "http", "fetch"]) and any(word in req_lower for word in ["web", "http", "url"]):
                    relevant_tools.append(tool_name)

            if relevant_tools:
                notes.append(f"Recommended tools for '{requirements}': {', '.join(relevant_tools)}")

        # Usage recommendations
        if len(tool_names) == 1:
            notes.append(f"Single tool setup - configure '{tool_names[0]}' directly")
        else:
            notes.append(f"Multiple tools available - consider using specific tools or 'all' for maximum flexibility")

        return notes

    def _create_error_result(self, component_type: str, error_msg: str) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            "status": "failed",
            "component_type": component_type,
            "discovered_capabilities": {
                "available_tools": [],
                "tool_count": 0,
                "connection_successful": False
            },
            "tool_schemas": {},
            "langflow_schemas": {},
            "recommendations": {
                "suggested_tools": [],
                "component_config": {},
                "integration_notes": [f"Discovery failed: {error_msg}"]
            },
            "errors": [error_msg]
        }

