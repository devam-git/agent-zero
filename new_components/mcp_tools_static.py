import json
import re
from typing import Any, Dict, List, Optional
import asyncio
from contextlib import AsyncExitStack

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

from langflow.custom.custom_component.component import Component
from langflow.base.mcp.util import create_tool_coroutine, create_tool_func, create_input_schema_from_json_schema
from langflow.io import (
    DropdownInput,
    IntInput,
    MessageTextInput,
    Output,
    DictInput,
)
from langflow.logging import logger
from langflow.schema.message import Message

# Import required for tools
from langchain_core.tools import StructuredTool
from langflow.field_typing import Tool


class MCPNodeClient:
    """MCP Client supporting SSE and HTTP connections."""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools: List[Any] = []
        self.server_url: Optional[str] = None
        self.http_headers: Dict[str, str] = {}
        self.http_client: Optional[httpx.AsyncClient] = None

    def _parse_response(self, response: httpx.Response) -> dict:
        """Parse response handling both JSON and SSE formats."""
        content_type = response.headers.get("content-type", "")

        if "text/event-stream" in content_type:
            text = response.text.strip()
            if not text:
                return {}
            lines = text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        return json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
            return {}
        else:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}

    async def connect_http(self, url: str, headers: Optional[Dict[str, str]] = None,
                          timeout_seconds: int = 30) -> List[Any]:
        """Connect to MCP server via HTTP transport."""
        if headers is None:
            headers = {}

        try:
            logger.info(f"Connecting to MCP server: {url}")

            request_headers = {
                **headers,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": "2025-03-26"
            }

            self.http_client = httpx.AsyncClient(timeout=timeout_seconds)
            self.server_url = url
            self.http_headers = request_headers

            # Initialize connection
            initialize_request = {
                "jsonrpc": "2.0",
                "id": "init-1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "langflow-mcp-tools", "version": "1.0.0"}
                }
            }

            init_response = await self.http_client.post(url, json=initialize_request, headers=request_headers)
            init_response.raise_for_status()
            init_result = self._parse_response(init_response)

            if "error" in init_result:
                raise ValueError(f"Initialization failed: {init_result['error']}")

            session_id = init_response.headers.get("Mcp-Session-Id")
            if session_id:
                self.http_headers["Mcp-Session-Id"] = session_id

            # List tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": "tools-list-1",
                "method": "tools/list",
                "params": {}
            }

            tools_response = await self.http_client.post(url, json=list_tools_request, headers=self.http_headers)
            tools_response.raise_for_status()
            tools_data = self._parse_response(tools_response)

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
                logger.info(f"Retrieved {len(tools)} tools")
                return tools
            elif "error" in tools_data:
                raise ValueError(f"Tools list failed: {tools_data['error']}")
            else:
                return []

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise ValueError(f"Connection failed: {e}")

    async def connect_sse(self, url: str, headers: Optional[Dict[str, str]] = None,
                          timeout_seconds: int = 30) -> List[Any]:
        """Connect via SSE."""
        if headers is None:
            headers = {}
        async with asyncio.timeout(timeout_seconds):
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(url, headers, timeout_seconds, timeout_seconds)
            )
            sse, write = sse_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(sse, write))
            await self.session.initialize()
            resp = await self.session.list_tools()
            self.tools = resp.tools
            return self.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool."""
        if self.session:
            return await self.session.call_tool(tool_name, arguments=arguments)
        elif self.http_client:
            import uuid
            req = {
                "jsonrpc": "2.0",
                "id": f"tool-call-{uuid.uuid4().hex[:8]}",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments}
            }
            resp = await self.http_client.post(self.server_url, json=req, headers=self.http_headers)
            resp.raise_for_status()
            result_data = resp.json().get("result", {})
            result = type("CallResult", (), {"content": []})()
            if "content" in result_data:
                for item in result_data["content"]:
                    result.content.append(type("Content", (), {"text": item.get("text", str(item))})())
            else:
                result.content.append(type("Content", (), {"text": str(result_data)})())
            return result
        else:
            raise ValueError("Not connected")

    async def run_tool(self, tool_name: str, arguments: dict):
        """Run tool - wrapper for utility functions."""
        return await self.call_tool(tool_name, arguments)


class MCPToolComponent(Component):
    display_name = "MCP Tools"
    description = "Connect to MCP servers and expose tools for agents (no dynamic updates)"
    icon = "QpiAI"
    name = "MCPTools"

    client = MCPNodeClient()
    tools: list = []

    inputs = [
        DropdownInput(
            name="connection_type",
            display_name="Connection Type",
            options=["http", "sse"],
            value="http",
            info="Connection type: http or sse"
        ),
        MessageTextInput(
            name="server_url",
            display_name="Server Endpoint",
            placeholder="http://localhost:3001 or http://localhost:3001/sse",
            info="MCP server endpoint URL (works for both http and sse)",
            value="",
            real_time_refresh=True
        ),
        DropdownInput(
            name="selected_tools",
            display_name="Selected Tools",
            options=["all"],
            value="all",
            info="Select 'all' for all tools or choose specific tool",
            show=True,
            real_time_refresh=True
        ),
        DictInput(
            name="headers",
            display_name="Headers",
            value={},
            advanced=True
        ),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (seconds)",
            value=30,
            advanced=True
        )
    ]

    outputs = [
        Output(display_name="Tools", name="component_as_tool", method="build_output")
    ]

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Update selected_tools dropdown when server_url changes."""
        try:
            if field_name == "server_url" and field_value and field_value.strip():
                # URL provided, try to get tools
                if not (field_value.startswith('http://') or field_value.startswith('https://')):
                    # Invalid URL, keep default
                    return build_config

                try:
                    # Get connection params
                    connection_type = getattr(self, 'connection_type', 'http')
                    headers = getattr(self, 'headers', {})
                    timeout = getattr(self, 'timeout_seconds', 30)

                    # Connect and get tools
                    if connection_type == "http":
                        tools = await self.client.connect_http(field_value, headers, timeout)
                    elif connection_type == "sse":
                        tools = await self.client.connect_sse(field_value, headers, timeout)
                    else:
                        tools = []

                    # Update dropdown options
                    tool_names = [t.name for t in tools if hasattr(t, 'name')]
                    build_config["selected_tools"]["options"] = ["all"] + tool_names
                    build_config["selected_tools"]["value"] = "all"

                except Exception as e:
                    logger.debug(f"Could not fetch tools: {e}")
                    # Keep default "all" option on error

        except Exception as e:
            logger.error(f"Error in update_build_config: {e}")

        return build_config

    async def build_output(self) -> list[Tool]:
        """Build and return tools."""
        try:
            server_url = getattr(self, 'server_url', '').strip()
            if not server_url:
                raise ValueError("Server URL is required")

            connection_type = getattr(self, 'connection_type', 'http')
            selected_tools = getattr(self, 'selected_tools', 'all').strip()
            headers = getattr(self, 'headers', {})
            timeout = getattr(self, 'timeout_seconds', 30)

            logger.info(f"Building MCP tools from {server_url} via {connection_type}")
            logger.info(f"Selected tools: {selected_tools}")

            # Connect and get tools
            if connection_type == "http":
                self.tools = await self.client.connect_http(server_url, headers, timeout)
            elif connection_type == "sse":
                self.tools = await self.client.connect_sse(server_url, headers, timeout)

            if not self.tools:
                raise ValueError("No tools found")

            # Filter tools
            if selected_tools == "all" or not selected_tools:
                filtered_tools = self.tools
            else:
                # Single tool selection
                filtered_tools = [t for t in self.tools if hasattr(t, 'name') and t.name == selected_tools]

            if not filtered_tools:
                raise ValueError(f"Tool not found: {selected_tools}")

            # Create Langflow tools
            tool_list = []
            for mcp_tool in filtered_tools:
                if hasattr(mcp_tool, 'name'):
                    try:
                        args_schema = create_input_schema_from_json_schema(
                            getattr(mcp_tool, 'inputSchema', {})
                        )

                        langflow_tool = StructuredTool(
                            name=mcp_tool.name,
                            description=getattr(mcp_tool, 'description', ''),
                            coroutine=create_tool_coroutine(mcp_tool.name, args_schema, self.client),
                            func=create_tool_func(mcp_tool.name, args_schema, self.client),
                            args_schema=args_schema,
                            handle_tool_error=True
                        )
                        tool_list.append(langflow_tool)
                        logger.debug(f"Created tool: {mcp_tool.name}")
                    except Exception as e:
                        logger.error(f"Failed to create tool {mcp_tool.name}: {e}")

            if not tool_list:
                raise ValueError("No tools created")

            logger.info(f"Successfully created {len(tool_list)} tools")
            return tool_list

        except Exception as e:
            error_msg = f"Failed to build tools: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def cleanup(self):
        """Cleanup."""
        try:
            await self.client.exit_stack.aclose()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")