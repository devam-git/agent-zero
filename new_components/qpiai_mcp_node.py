import json
import re
from typing import Any, Dict, List, Optional, Union
import asyncio
from contextlib import AsyncExitStack

import httpx
from mcp import ClientSession, types
from mcp.client.sse import sse_client

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
    if not any(re.search(r"\.|\\[\\d+\\]", key) for key in flat):
        return flat

    nested: Dict[str, Any] = {}
    array_re = re.compile(r"^(.+)\\[(\\d+)\\]$")

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


class SSEOptimizedMCPClient:
    """MCP client optimized for SSE connection issues"""

    def __init__(self):
        # Connection state
        self.session: Optional[ClientSession] = None
        self.sse = None
        self.write = None
        self.exit_stack = AsyncExitStack()

        # Connection management
        self._connection_lock = asyncio.Lock()

        # Timeouts based on diagnostic results
        self.basic_timeout = 7      # Basic connectivity (5s + 2s safety)
        self.sse_timeout = 25       # SSE streaming needs more time
        self.operation_timeout = 10 # Individual operations
        self.retry_delay = 2        # Delay between retries

    async def _wait_for_server_ready(self, url: str) -> bool:
        """Wait for server to be ready before attempting SSE"""
        logger.debug("Checking if server is ready for SSE connection")

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.basic_timeout) as client:
                    response = await client.head(url)
                    if response.status_code == 200:
                        logger.debug(f"Server ready on attempt {attempt + 1}")
                        return True
            except Exception as e:
                logger.debug(f"Server readiness check {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)  # Brief wait between checks

        return False

    async def _create_sse_connection_with_retries(self, url: str, headers: Optional[dict[str, str]] = None) -> list[types.Tool]:
        """Create SSE connection with specific retry strategy for SSE issues"""
        if headers is None:
            headers = {}

        logger.info(f"Creating SSE connection with retries to: {url}")
        await self._cleanup_connection()

        # Wait for server to be ready first
        if not await self._wait_for_server_ready(url):
            raise ValueError("Server not responding to readiness checks")

        # Try SSE connection with progressive timeouts
        sse_timeouts = [15, 25, 35]  # Progressive SSE timeouts

        for attempt, sse_timeout in enumerate(sse_timeouts):
            try:
                logger.info(f"SSE attempt {attempt + 1}/{len(sse_timeouts)} with {sse_timeout}s timeout")

                async with asyncio.timeout(sse_timeout + 5):  # Add buffer to asyncio timeout
                    # Create SSE client with current timeout
                    sse_transport = await self.exit_stack.enter_async_context(
                        sse_client(url, headers, self.basic_timeout, sse_timeout)
                    )
                    self.sse, self.write = sse_transport
                    logger.debug(f"SSE transport created with {sse_timeout}s timeout")

                    # Create and initialize session quickly
                    async with asyncio.timeout(self.operation_timeout):
                        self.session = await self.exit_stack.enter_async_context(
                            ClientSession(self.sse, self.write)
                        )
                        await self.session.initialize()
                        logger.debug("Session initialized successfully")

                    # Get tools quickly
                    async with asyncio.timeout(self.operation_timeout):
                        response = await self.session.list_tools()
                        logger.info(f"Successfully connected with {sse_timeout}s timeout, found {len(response.tools)} tools")
                        return response.tools

            except asyncio.TimeoutError:
                logger.warning(f"SSE attempt {attempt + 1} timed out after {sse_timeout}s")
                await self._cleanup_connection()
                if attempt < len(sse_timeouts) - 1:
                    logger.info(f"Waiting {self.retry_delay}s before next attempt")
                    await asyncio.sleep(self.retry_delay)
                continue

            except Exception as e:
                logger.warning(f"SSE attempt {attempt + 1} failed: {str(e)}")
                await self._cleanup_connection()
                if attempt < len(sse_timeouts) - 1:
                    # For non-timeout errors, wait a bit longer
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"Waiting {wait_time}s before next attempt")
                    await asyncio.sleep(wait_time)
                continue

        # All attempts failed
        raise ValueError("All SSE connection attempts failed - server may be overloaded")

    async def _cleanup_connection(self):
        """Clean up connection resources"""
        try:
            if self.exit_stack:
                await asyncio.wait_for(self.exit_stack.aclose(), timeout=5)
        except Exception as e:
            logger.debug(f"Cleanup error (ignored): {e}")
        finally:
            self.session = None
            self.sse = None
            self.write = None
            self.exit_stack = AsyncExitStack()

    async def _is_session_healthy(self) -> bool:
        """Quick health check"""
        if not self.session:
            return False
        try:
            async with asyncio.timeout(5):
                await self.session.list_tools()
                return True
        except Exception:
            return False

    async def get_tools_optimized(self, url: str, headers: Optional[dict[str, str]] = None) -> list[types.Tool]:
        """Get tools with SSE optimization"""
        async with self._connection_lock:
            try:
                # Check if existing session is healthy
                if self.session and await self._is_session_healthy():
                    logger.debug("Using existing healthy session")
                    async with asyncio.timeout(self.operation_timeout):
                        response = await self.session.list_tools()
                        return response.tools

                # Need new connection
                logger.info("Creating new SSE-optimized connection")
                return await self._create_sse_connection_with_retries(url, headers)

            except Exception as e:
                await self._cleanup_connection()
                raise ValueError(f"Optimized connection failed: {str(e)}")

    async def close(self):
        """Close connection"""
        async with self._connection_lock:
            await self._cleanup_connection()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool with arguments."""
        if not self.session:
            raise ValueError("Session not initialized. Call get_tools_optimized first.")

        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)
            return result
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {e}")
            raise


class QpiAIMCPNode(Component):
    """QpiAI MCP Node Component - Use QpiAI MCP server tools directly as nodes without agents."""

    display_name = "QpiAI MCP Node"
    description = "Connect to QpiAI hosted MCP servers and use their tools directly as workflow nodes"
    icon = "QpiAI"
    name = "QpiAIMCPNode"

    # Use same pattern as MCPNodeComponent
    schema_inputs: list = []
    client = SSEOptimizedMCPClient()
    tools: list = []
    _tool_cache: dict = {}
    default_keys: list[str] = [
        "code",
        "_type",
        "tool_api_url",
        "tool_api_credentials",
        "tool_name",
        "selected_tool",
        "output_format"
    ]

    inputs = [
        MessageTextInput(
            name="tool_api_url",
            display_name="Tool API URL",
            info="QpiAI tool API base URL",
            value="",
            tool_mode=False,
            real_time_refresh=True,
        ),
        MessageTextInput(
            name="tool_api_credentials",
            display_name="Tool API Credentials",
            info="QpiAI API credentials",
            value="",
            tool_mode=False,
            real_time_refresh=True,
        ),
        MessageTextInput(
            name="tool_name",
            display_name="Service Name",
            info="QpiAI service name (e.g., gmail, slack)",
            value="gmail",
            tool_mode=False,
            real_time_refresh=True,
        ),
        DropdownInput(
            name="selected_tool",
            display_name="Tool",
            options=[],
            value="",
            info="Select the specific tool to execute",
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
        """Update available tools from QpiAI MCP server."""
        try:
            tool_api_url = getattr(self, 'tool_api_url', '')
            tool_name = getattr(self, 'tool_name', '')
            tool_api_credentials = getattr(self, 'tool_api_credentials', '')

            if not tool_api_url or not tool_name or not tool_api_credentials:
                self.tools = []
                return []

            url = f"{tool_api_url}/{tool_name}/{tool_api_credentials}"
            self.tools = await self.client.get_tools_optimized(url)

            # Cache tools for execution
            self._tool_cache = {tool.name: tool for tool in self.tools if hasattr(tool, 'name')}
            return self.tools

        except Exception as e:
            logger.error(f"Failed to update tool list: {e}")
            self.tools = []
            self._tool_cache = {}
            raise ValueError(f"Connection failed: {str(e)}")

    def get_inputs_for_all_tools(self, tools: list) -> dict:
        """Get input schemas for all tools - same pattern as MCPNodeComponent."""
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
        """Remove the input schema for the tool from the build config - same as MCPNodeComponent."""
        # Keep only schemas that don't belong to the current tool
        input_schema = {k: v for k, v in input_schema.items() if k != tool_name}
        # Remove all inputs from other tools
        for value in input_schema.values():
            for _input in value:
                if _input.name in build_config:
                    build_config.pop(_input.name)

    def remove_non_default_keys(self, build_config: dict) -> None:
        """Remove non-default keys from the build config - same as MCPNodeComponent."""
        for key in list(build_config.keys()):
            if key not in self.default_keys:
                build_config.pop(key)

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Update build configuration based on field changes - based on MCPNodeComponent pattern."""
        try:
            if field_name in ["tool_api_url", "tool_api_credentials", "tool_name"]:
                # Connection parameters changed, update tool list
                tool_api_url = getattr(self, 'tool_api_url', '') if field_name != 'tool_api_url' else field_value
                tool_name = getattr(self, 'tool_name', '') if field_name != 'tool_name' else field_value
                tool_api_credentials = getattr(self, 'tool_api_credentials', '') if field_name != 'tool_api_credentials' else field_value

                if not tool_api_url or not tool_name or not tool_api_credentials:
                    # Missing required fields, hide tools
                    build_config["selected_tool"]["show"] = False
                    build_config["selected_tool"]["options"] = []
                    build_config["selected_tool"]["value"] = ""
                    self.remove_non_default_keys(build_config)
                    return build_config

                # Set the current values to ensure update_tool_list has them
                if field_name == 'tool_api_url':
                    self.tool_api_url = field_value
                elif field_name == 'tool_name':
                    self.tool_name = field_value
                elif field_name == 'tool_api_credentials':
                    self.tool_api_credentials = field_value

                try:
                    tools = await self.update_tool_list()
                    tool_names = [tool.name for tool in tools if hasattr(tool, 'name')]

                    build_config["selected_tool"]["options"] = tool_names
                    build_config["selected_tool"]["show"] = len(tool_names) > 0
                    build_config["selected_tool"]["value"] = tool_names[0] if tool_names else ""
                    build_config["selected_tool"]["placeholder"] = "Select a tool"

                    # Remove previous dynamic inputs
                    self.remove_non_default_keys(build_config)

                    # If we have a default tool, generate its inputs
                    if tool_names:
                        await self._update_tool_config(build_config, tool_names[0])

                except Exception as e:
                    logger.error(f"Failed to update tool list: {e}")
                    build_config["selected_tool"]["show"] = True
                    build_config["selected_tool"]["options"] = ["❌ Connection Failed"]
                    build_config["selected_tool"]["value"] = "❌ Connection Failed"
                    build_config["selected_tool"]["placeholder"] = f"Error: {str(e)[:150]}..."
                    self.remove_non_default_keys(build_config)

            elif field_name == "selected_tool" and field_value:
                # Tool selection changed, update dynamic inputs
                if field_value in ["❌ Connection Error", "❌ Connection Failed"]:
                    return build_config

                # Clear old inputs and update with new tool
                await self._update_tool_config(build_config, field_value)

        except Exception as e:
            logger.error(f"Error in update_build_config: {e}")

        return build_config

    async def _update_tool_config(self, build_config: dict, tool_name: str) -> None:
        """Update tool configuration - based on MCPNodeComponent pattern."""
        if not self.tools:
            self.tools = await self.update_tool_list()

        if not tool_name:
            return

        tool_obj = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool_obj:
            self.remove_non_default_keys(build_config)
            build_config["selected_tool"]["value"] = ""
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
        """Execute the selected QpiAI MCP tool with provided inputs - based on MCPNodeComponent pattern."""
        try:
            selected_tool = getattr(self, 'selected_tool', '')
            if not selected_tool or selected_tool in ["❌ Connection Error", "❌ Connection Failed"]:
                return Message(text="No valid tool selected")

            # Get tool from cache
            if selected_tool not in self._tool_cache:
                # Reconnect and update cache
                await self.update_tool_list()

            if selected_tool not in self._tool_cache:
                return Message(text=f"Tool '{selected_tool}' not found")

            exec_tool = self._tool_cache[selected_tool]

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
            result = await self.client.call_tool(selected_tool, unflattened_kwargs)

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
                        text_content = "\\n".join(str(item) for item in content_items)
                        return Message(text=text_content)
                elif output_format == "data":
                    return Data(data={
                        "tool_name": selected_tool,
                        "result": content_items,
                        "arguments": unflattened_kwargs,
                        "raw_result": str(result)
                    })
                else:  # auto
                    if len(content_items) == 1 and isinstance(content_items[0], str):
                        return Message(text=content_items[0])
                    else:
                        return Data(data={
                            "tool_name": selected_tool,
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
                        "tool_name": selected_tool,
                        "result": result_str,
                        "arguments": unflattened_kwargs,
                        "raw_result": result
                    })

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg)
            return Message(text=error_msg)

    async def cleanup(self):
        """Cleanup for Langflow"""
        try:
            await self.client.close()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")