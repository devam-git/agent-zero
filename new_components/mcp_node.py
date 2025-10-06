import json
import re
from typing import Any, Dict, List, Optional, Union
import asyncio
from contextlib import AsyncExitStack

import httpx
from mcp import ClientSession, types
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from langflow.custom.custom_component.component import Component
from langflow.io import (
    BoolInput,
    DropdownInput,
    IntInput,
    MessageTextInput,
    MultilineInput,
    Output,
    StrInput,
    DictInput,
    FloatInput
)
from langflow.logging import logger
from langflow.schema.data import Data
from langflow.schema.message import Message


def maybe_unflatten_dict(flat: Dict[str, Any]) -> Dict[str, Any]:
    """Convert flat dictionary with dot notation keys to nested structure."""
    if not any(re.search(r"\.|\[\d+\]", key) for key in flat):
        return flat

    nested: Dict[str, Any] = {}
    array_re = re.compile(r"^(.+)\[(\d+)\]$")

    for key, val in flat.items():
        parts = key.split(".")
        cur = nested
        for i, part in enumerate(parts):
            m = array_re.match(part)
            if m:
                name, idx = m.group(1), int(m.group(2))
                lst = cur.setdefault(name, [])
                while len(lst) <= idx:
                    lst.append({})
                if i == len(parts) - 1:
                    lst[idx] = val
                else:
                    cur = lst[idx]
            elif i == len(parts) - 1:
                cur[part] = val
            else:
                cur = cur.setdefault(part, {})

    return nested


class MCPNodeClient:
    """MCP Client for both SSE and stdio connections."""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools: List[Any] = []
        self.server_url: Optional[str] = None
        self.session_id: Optional[str] = None
        self.http_headers: Dict[str, str] = {}
        self.http_client: Optional[httpx.AsyncClient] = None

    def _parse_response(self, response: httpx.Response) -> dict:
        """Parse response handling both JSON and SSE formats."""
        content_type = response.headers.get("content-type", "")

        if "text/event-stream" in content_type:
            # Handle SSE response
            text = response.text.strip()
            if not text:
                return {}

            # Parse SSE format: "event: message\ndata: {json}\n"
            lines = text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        return json.loads(line[6:])  # Remove "data: " prefix
                    except json.JSONDecodeError:
                        continue
            return {}
        else:
            # Handle JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}

    async def connect_http(self, url: str, headers: Optional[Dict[str, str]] = None,
                          timeout_seconds: int = 30) -> List[Any]:
        """Connect to MCP server via HTTP transport (handles both JSON and SSE responses)."""
        if headers is None:
            headers = {}

        try:
            logger.info(f"=== MCP HTTP Connection Attempt ===")
            logger.info(f"URL: {url}")
            logger.info(f"Additional headers: {headers}")

            # MCP HTTP transport headers as per specification
            request_headers = {
                **headers,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": "2025-03-26"
            }
            logger.info(f"Request headers: {request_headers}")

            # Create persistent HTTP client
            self.http_client = httpx.AsyncClient(timeout=timeout_seconds)
            self.server_url = url
            self.http_headers = request_headers

            # Step 1: Initialize connection
            initialize_request = {
                "jsonrpc": "2.0",
                "id": "init-1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "langflow-mcp-node",
                        "version": "1.0.0"
                    }
                }
            }

            logger.info(f"Sending initialize request to {url}")
            init_response = await self.http_client.post(url, json=initialize_request, headers=request_headers)
            init_response.raise_for_status()

            # Handle both JSON and SSE responses
            init_result = self._parse_response(init_response)
            logger.info(f"Initialize response: {init_result}")

            if "error" in init_result:
                raise ValueError(f"Initialization failed: {init_result['error']}")

            # Extract session ID if provided
            session_id = init_response.headers.get("Mcp-Session-Id")
            if session_id:
                logger.info(f"Got session ID: {session_id}")
                self.http_headers["Mcp-Session-Id"] = session_id
                self.session_id = session_id

            # Step 2: List tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": "tools-list-1",
                "method": "tools/list",
                "params": {}
            }

            logger.info("Sending tools/list request")
            tools_response = await self.http_client.post(url, json=list_tools_request, headers=self.http_headers)
            tools_response.raise_for_status()

            # Handle both JSON and SSE responses
            tools_data = self._parse_response(tools_response)
            logger.info(f"Tools response: {tools_data}")

            # Process tools response
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools = []
                for tool_data in tools_data["result"]["tools"]:
                    tool_obj = type('Tool', (), {
                        'name': tool_data.get('name'),
                        'description': tool_data.get('description', ''),
                        'inputSchema': tool_data.get('inputSchema', {})
                    })()
                    tools.append(tool_obj)

                self.tools = tools
                logger.info(f"Successfully retrieved {len(tools)} tools")
                return tools
            elif "error" in tools_data:
                raise ValueError(f"Tools list failed: {tools_data['error']}")
            else:
                logger.warning("No tools found in response")
                return []

        except httpx.HTTPStatusError as e:
            error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            logger.error(f"HTTP {e.response.status_code}: {error_text}")

            # If we get 500 with "Server got itself in trouble", try different URLs
            if e.response.status_code == 500 and "trouble" in error_text:
                # Try without /http/ suffix
                if url.endswith('/http/'):
                    logger.info("Trying without /http/ suffix...")
                    return await self.connect_http(url[:-6], headers, timeout_seconds)
                # Try with different suffix
                elif not url.endswith('/'):
                    logger.info("Trying with trailing slash...")
                    return await self.connect_http(url + '/', headers, timeout_seconds)

            raise ValueError(f"HTTP {e.response.status_code}: {error_text}")
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise ValueError(f"Connection failed: {e}")
        except Exception as e:
            logger.error(f"HTTP connection failed: {e}")
            raise ValueError(f"Connection failed: {e}")

    async def connect_sse(self, url: str, headers: Optional[Dict[str, str]] = None,
                         timeout_seconds: int = 30) -> List[Any]:
        """Connect to MCP server via SSE."""
        if headers is None:
            headers = {}

        try:
            # Check for redirects
            async with httpx.AsyncClient(follow_redirects=False) as client:
                response = await client.request("HEAD", url)
                if response.status_code == 307:
                    url = response.headers.get("Location", url)

            async with asyncio.timeout(timeout_seconds):
                sse_transport = await self.exit_stack.enter_async_context(
                    sse_client(url, headers, timeout_seconds, timeout_seconds)
                )
                sse, write = sse_transport
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(sse, write)
                )
                await self.session.initialize()
                response = await self.session.list_tools()
                self.tools = response.tools
                return self.tools

        except Exception as e:
            logger.error(f"Failed to connect via SSE: {e}")
            raise

    async def connect_stdio(self, command: str, args: Optional[List[str]] = None,
                           timeout_seconds: int = 30) -> List[Any]:
        """Connect to MCP server via stdio."""
        if args is None:
            args = []

        try:
            async with asyncio.timeout(timeout_seconds):
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(command, args)
                )
                stdio_read, stdio_write = stdio_transport
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(stdio_read, stdio_write)
                )
                await self.session.initialize()
                response = await self.session.list_tools()
                self.tools = response.tools
                return self.tools

        except Exception as e:
            logger.error(f"Failed to connect via stdio: {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool with arguments."""
        try:
            # Check if we have a session (SSE) or HTTP client (Streamable HTTP)
            if self.session:
                # Use session for SSE connections
                result = await self.session.call_tool(tool_name, arguments=arguments)
                return result
            elif hasattr(self, 'http_client') and self.http_client:
                # Use HTTP client for HTTP connections
                import uuid
                call_request = {
                    "jsonrpc": "2.0",
                    "id": f"tool-call-{uuid.uuid4().hex[:8]}",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }

                response = await self.http_client.post(self.server_url, json=call_request, headers=self.http_headers)
                response.raise_for_status()
                result_data = self._parse_response(response)

                if "error" in result_data:
                    raise ValueError(f"Tool call failed: {result_data['error']}")

                # Create a mock result object that matches MCP client expectations
                result = type('CallResult', (), {
                    'content': []
                })()

                if "result" in result_data:
                    # Handle different result formats
                    result_content = result_data["result"]
                    if isinstance(result_content, dict) and "content" in result_content:
                        # Standard MCP response format
                        content_items = result_content["content"]
                        for item in content_items:
                            content_obj = type('Content', (), {
                                'text': item.get('text', str(item))
                            })()
                            result.content.append(content_obj)
                    else:
                        # Simple response format
                        content_obj = type('Content', (), {
                            'text': str(result_content)
                        })()
                        result.content.append(content_obj)

                return result
            else:
                raise ValueError("Not connected to MCP server")

        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {e}")
            raise


class MCPNodeComponent(Component):
    """MCP Node Component - Use MCP server tools directly as nodes without agents."""

    display_name = "MCP Node"
    description = "Connect to MCP servers and use their tools directly as workflow nodes"
    icon = "QpiAI"
    name = "MCPNode"

    # Use exact same pattern as MCPToolsComponent
    schema_inputs: list = []
    client = MCPNodeClient()
    tools: list = []
    _tool_cache: dict = {}
    default_keys: list[str] = [
        "code",
        "_type",
        "connection_type",
        "server_url",
        "stdio_command",
        "stdio_args",
        "headers",
        "timeout_seconds",
        "tool_name",
        "output_format"
    ]

    inputs = [
        DropdownInput(
            name="connection_type",
            display_name="Connection Type",
            options=["http", "sse"],
            value="http",
            info="MCP transport type (http: Standard HTTP JSON-RPC, sse: Server-Sent Events)",
            real_time_refresh=True
        ),
        MessageTextInput(
            name="server_url",
            display_name="Server URL",
            info="MCP server URL (paste your full URL here)",
            placeholder="https://your-server.com/mcp",
            show=True,
            real_time_refresh=True
        ),
        MessageTextInput(
            name="stdio_command",
            display_name="Command",
            info="Command to run for stdio connection (e.g., 'python', 'node')",
            placeholder="python",
            show=False,
            real_time_refresh=True
        ),
        MessageTextInput(
            name="stdio_args",
            display_name="Arguments",
            info="Command arguments separated by spaces",
            placeholder="server.py",
            show=False,
            advanced=True
        ),
        DictInput(
            name="headers",
            display_name="Headers",
            info="HTTP headers for connection",
            value={},
            show=False,
            advanced=True
        ),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (seconds)",
            info="Connection timeout",
            value=30,
            advanced=True
        ),
        DropdownInput(
            name="tool_name",
            display_name="Tool",
            options=[],
            value="",
            info="Select the MCP tool to execute",
            show=False,
            real_time_refresh=True
        ),
        DropdownInput(
            name="output_format",
            display_name="Output Format",
            options=["auto", "message", "data"],
            value="auto",
            info="Format for the output (auto: smart detection, message: text only, data: structured)",
            advanced=True
        ),
    ]

    outputs = [
        Output(display_name="Result", name="result", method="build_output"),
    ]

    async def update_tool_list(self):
        """Update available tools from MCP server."""
        try:
            # Connect based on connection type
            if self.connection_type == "http":
                url = getattr(self, 'server_url', '')
                if not url:
                    self.tools = []
                    return []
                headers = getattr(self, 'headers', {})
                timeout = getattr(self, 'timeout_seconds', 30)
                self.tools = await self.client.connect_http(url, headers, timeout)
            elif self.connection_type == "sse":
                url = getattr(self, 'server_url', '')
                if not url:
                    self.tools = []
                    return []
                headers = getattr(self, 'headers', {})
                timeout = getattr(self, 'timeout_seconds', 30)
                self.tools = await self.client.connect_sse(url, headers, timeout)

            # Cache tools for execution
            self._tool_cache = {tool.name: tool for tool in self.tools if hasattr(tool, 'name')}
            return self.tools

        except Exception as e:
            logger.error(f"Failed to update tool list: {e}")
            self.tools = []
            self._tool_cache = {}
            raise ValueError(f"Connection failed: {str(e)}")

    def get_inputs_for_all_tools(self, tools: list) -> dict:
        """Get input schemas for all tools - same pattern as MCPToolsComponent."""
        inputs = {}
        for tool in tools:
            if not tool or not hasattr(tool, "name"):
                continue
            try:
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    input_schema = tool.inputSchema
                    langflow_inputs = self.schema_to_langflow_inputs(input_schema)
                    inputs[tool.name] = langflow_inputs
            except (AttributeError, ValueError, TypeError, KeyError) as e:
                logger.error(f"Error getting inputs for tool {getattr(tool, 'name', 'unknown')}: {e}")
                continue
        return inputs

    def schema_to_langflow_inputs(self, input_schema: dict) -> list:
        """Convert tool input schema to Langflow inputs."""
        langflow_inputs = []

        if not input_schema or "properties" not in input_schema:
            return langflow_inputs

        properties = input_schema["properties"]
        required_fields = input_schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            is_required = prop_name in required_fields
            input_field = self.json_schema_to_langflow_input(prop_name, prop_schema, is_required)
            if input_field:
                langflow_inputs.append(input_field)

        return langflow_inputs

    def json_schema_to_langflow_input(self, name: str, schema: dict, required: bool = False):
        """Convert JSON schema property to Langflow input."""
        schema_type = schema.get("type", "string")
        description = schema.get("description", "")
        default = schema.get("default")
        enum_values = schema.get("enum")

        # Build common params carefully to avoid duplicates
        common_params = {
            "name": name,
            "display_name": name.replace("_", " ").title(),
            "required": required,
            "show": True
        }

        # Only add description if it exists
        if description:
            common_params["info"] = description

        # Only add default if it exists and is not None
        if default is not None:
            common_params["value"] = default

        # Handle enum/choices
        if enum_values:
            return DropdownInput(
                options=[str(v) for v in enum_values],
                **common_params
            )

        # Handle different types
        if schema_type == "string":
            if schema.get("format") == "textarea" or len(description) > 100:
                return MultilineInput(**common_params)
            else:
                return MessageTextInput(**common_params)
        elif schema_type == "integer":
            return IntInput(**common_params)
        elif schema_type == "number":
            return FloatInput(**common_params)
        elif schema_type == "boolean":
            return BoolInput(**common_params)
        elif schema_type == "object":
            return DictInput(**common_params)
        elif schema_type == "array":
            # For arrays, create a copy of common_params and modify info
            array_params = common_params.copy()
            array_info = f"{description} (JSON array format)" if description else "JSON array format"
            array_params["info"] = array_info
            return MessageTextInput(**array_params)
        else:
            return MessageTextInput(**common_params)

    def remove_input_schema_from_build_config(self, build_config: dict, tool_name: str, input_schema: dict):
        """Remove the input schema for the tool from the build config - same as MCPToolsComponent."""
        # Keep only schemas that don't belong to the current tool
        input_schema = {k: v for k, v in input_schema.items() if k != tool_name}
        # Remove all inputs from other tools
        for value in input_schema.values():
            for _input in value:
                if _input.name in build_config:
                    build_config.pop(_input.name)

    def remove_non_default_keys(self, build_config: dict) -> None:
        """Remove non-default keys from the build config - same as MCPToolsComponent."""
        for key in list(build_config.keys()):
            if key not in self.default_keys:
                build_config.pop(key)

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Update build configuration based on field changes - based on MCPToolsComponent pattern."""
        try:
            if field_name == "connection_type":
                # Show/hide connection-specific fields
                is_http_based = field_value in ["http", "sse"]
                build_config["server_url"]["show"] = is_http_based
                build_config["stdio_command"]["show"] = False  # Removed stdio support
                build_config["stdio_args"]["show"] = False    # Removed stdio support
                build_config["headers"]["show"] = is_http_based

                # Update labels and info based on connection type
                if field_value == "http":
                    build_config["server_url"]["display_name"] = "HTTP Endpoint"
                    build_config["server_url"]["info"] = "MCP HTTP endpoint (e.g., http://localhost:8000/mcp)"
                    build_config["server_url"]["placeholder"] = "http://localhost:8000/mcp"
                elif field_value == "sse":
                    build_config["server_url"]["display_name"] = "SSE Server URL"
                    build_config["server_url"]["info"] = "Server-Sent Events endpoint (e.g., http://localhost:8000/sse)"
                    build_config["server_url"]["placeholder"] = "http://localhost:8000/sse"

                # Hide tool selection until connection is made
                build_config["tool_name"]["show"] = False
                build_config["tool_name"]["options"] = []
                build_config["tool_name"]["value"] = ""

                # Remove any dynamic inputs
                self.remove_non_default_keys(build_config)

            elif field_name in ["server_url", "stdio_command", "stdio_args"]:
                # Connection parameters changed, update tool list
                if field_name == "server_url":
                    if not field_value or not field_value.strip():
                        # Empty URL, hide tools
                        build_config["tool_name"]["show"] = False
                        build_config["tool_name"]["options"] = []
                        build_config["tool_name"]["value"] = ""
                        self.remove_non_default_keys(build_config)
                        return build_config

                    # Basic URL validation to prevent disappearing
                    if not (field_value.startswith('http://') or field_value.startswith('https://')):
                        logger.warning(f"URL should start with http:// or https://: {field_value}")
                        build_config["tool_name"]["show"] = False
                        build_config["tool_name"]["options"] = ["❌ Invalid URL"]
                        build_config["tool_name"]["value"] = "❌ Invalid URL"
                        self.remove_non_default_keys(build_config)
                        return build_config

                if field_name == "stdio_command" and not field_value.strip():
                    # Empty command, hide tools
                    build_config["tool_name"]["show"] = False
                    build_config["tool_name"]["options"] = []
                    build_config["tool_name"]["value"] = ""
                    self.remove_non_default_keys(build_config)
                    return build_config

                try:
                    tools = await self.update_tool_list()
                    tool_names = [tool.name for tool in tools if hasattr(tool, 'name')]

                    build_config["tool_name"]["options"] = tool_names
                    build_config["tool_name"]["show"] = len(tool_names) > 0
                    build_config["tool_name"]["value"] = tool_names[0] if tool_names else ""
                    build_config["tool_name"]["placeholder"] = "Select a tool"

                    # Remove previous dynamic inputs
                    self.remove_non_default_keys(build_config)

                    # If we have a default tool, generate its inputs
                    if tool_names:
                        await self._update_tool_config(build_config, tool_names[0])

                except Exception as e:
                    logger.error(f"Failed to update tool list: {e}")
                    build_config["tool_name"]["show"] = True
                    build_config["tool_name"]["options"] = ["❌ Connection Failed"]
                    build_config["tool_name"]["value"] = "❌ Connection Failed"
                    build_config["tool_name"]["placeholder"] = f"Error: {str(e)[:150]}..."
                    self.remove_non_default_keys(build_config)

            elif field_name == "tool_name" and field_value:
                # Tool selection changed, update dynamic inputs
                if field_value in ["❌ Connection Error", "❌ Connection Failed"]:
                    return build_config

                # Clear old inputs and update with new tool
                await self._update_tool_config(build_config, field_value)

        except Exception as e:
            logger.error(f"Error in update_build_config: {e}")

        return build_config

    async def _update_tool_config(self, build_config: dict, tool_name: str) -> None:
        """Update tool configuration - based on MCPToolsComponent pattern."""
        if not self.tools:
            self.tools = await self.update_tool_list()

        if not tool_name:
            return

        tool_obj = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool_obj:
            self.remove_non_default_keys(build_config)
            build_config["tool_name"]["value"] = ""
            return

        try:
            # Store current values before removing inputs
            current_values = {}
            for key, value in build_config.items():
                if key not in self.default_keys and isinstance(value, dict) and "value" in value:
                    current_values[key] = value["value"]

            # Get all tool inputs and remove old ones
            input_schema_for_all_tools = self.get_inputs_for_all_tools(self.tools)
            self.remove_input_schema_from_build_config(build_config, tool_name, input_schema_for_all_tools)

            # Get and validate new inputs
            self.schema_inputs = self.schema_to_langflow_inputs(tool_obj.inputSchema if hasattr(tool_obj, 'inputSchema') else {})
            if not self.schema_inputs:
                return

            # Add new inputs to build config
            for schema_input in self.schema_inputs:
                if not schema_input or not hasattr(schema_input, "name"):
                    continue

                try:
                    name = schema_input.name
                    input_dict = schema_input.to_dict()

                    # Clean up the input_dict to avoid duplicates
                    input_dict.setdefault("value", None)
                    input_dict.setdefault("required", True)

                    # Ensure no duplicate keys that could cause conflicts
                    if "info" not in input_dict:
                        input_dict["info"] = ""

                    build_config[name] = input_dict

                    # Preserve existing value if the parameter name exists in current_values
                    if name in current_values:
                        build_config[name]["value"] = current_values[name]

                except (AttributeError, KeyError, TypeError) as e:
                    logger.error(f"Error processing schema input {schema_input}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing schema input {getattr(schema_input, 'name', 'unknown')}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error updating tool config: {e}")
            self.schema_inputs = []

    async def build_output(self) -> Union[Message, Data]:
        """Execute the selected MCP tool with provided inputs - based on MCPToolsComponent pattern."""
        try:
            tool_name = getattr(self, 'tool_name', '')
            if not tool_name or tool_name in ["❌ Connection Error", "❌ Connection Failed"]:
                return Message(text="No valid tool selected")

            # Get tool from cache
            if tool_name not in self._tool_cache:
                # Reconnect and update cache
                await self.update_tool_list()

            if tool_name not in self._tool_cache:
                return Message(text=f"Tool '{tool_name}' not found")

            exec_tool = self._tool_cache[tool_name]

            # Collect arguments
            tool_args = self.schema_to_langflow_inputs(exec_tool.inputSchema if hasattr(exec_tool, 'inputSchema') else {})
            kwargs = {}

            for arg in tool_args:
                value = getattr(self, arg.name, None)
                if value is not None and value != "":
                    # Handle JSON parsing for arrays/objects
                    if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass  # Keep as string
                    kwargs[arg.name] = value

            # Unflatten arguments
            unflattened_kwargs = maybe_unflatten_dict(kwargs)

            # Execute tool
            result = await self.client.call_tool(tool_name, unflattened_kwargs)

            # Process result based on output format
            output_format = getattr(self, 'output_format', 'auto')

            if hasattr(result, 'content') and result.content:
                # Extract content from MCP response
                content_items = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_items.append(item.text)
                    elif hasattr(item, 'model_dump'):
                        content_items.append(item.model_dump())
                    else:
                        content_items.append(str(item))

                # Handle output formatting
                if output_format == "message":
                    if len(content_items) == 1 and isinstance(content_items[0], str):
                        return Message(text=content_items[0])
                    else:
                        text_content = "\n".join(str(item) for item in content_items)
                        return Message(text=text_content)
                elif output_format == "data":
                    return Data(data={
                        "tool_name": tool_name,
                        "result": content_items,
                        "arguments": unflattened_kwargs,
                        "raw_result": str(result)
                    })
                else:  # auto
                    if len(content_items) == 1 and isinstance(content_items[0], str):
                        return Message(text=content_items[0])
                    else:
                        return Data(data={
                            "tool_name": tool_name,
                            "result": content_items,
                            "arguments": unflattened_kwargs
                        })
            else:
                # No content
                result_str = str(result)
                if output_format == "message":
                    return Message(text=result_str)
                else:
                    return Data(data={
                        "tool_name": tool_name,
                        "result": result_str,
                        "arguments": unflattened_kwargs,
                        "raw_result": result
                    })

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg)
            return Message(text=error_msg)