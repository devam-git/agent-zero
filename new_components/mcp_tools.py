import json
import re
from typing import Any, Dict, List, Optional, Union
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
from langflow.schema.data import Data
from langflow.schema.message import Message

# Import required for tools
from langchain_core.tools import StructuredTool
from langflow.field_typing import Tool


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
        if self.session:
            return await self.session.call_tool(tool_name, arguments=arguments)
        elif self.http_client:
            import uuid
            req = {"jsonrpc": "2.0", "id": f"tool-call-{uuid.uuid4().hex[:8]}", "method": "tools/call", "params": {"name": tool_name, "arguments": arguments}}
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
            raise ValueError("Not connected to MCP server")

    async def run_tool(self, tool_name: str, arguments: dict):
        """Run a tool with the given arguments - this is what the utility functions expect"""
        return await self.call_tool(tool_name, arguments)


class MCPToolComponent(Component):
    display_name = "MCP Tools"
    description = "Connect to MCP servers and expose selected tools for agent integration"
    icon = "QpiAI"
    name = "MCPTools" 

    client = MCPNodeClient()
    tools: list = []
    _tool_cache: dict = {}
    default_keys: list[str] = [
        "code", "_type", "connection_type", "server_url", "headers", "timeout_seconds", "selected_tools"
    ]

    inputs = [
        DropdownInput(name="connection_type", display_name="Connection Type", options=["http", "sse"], value="http", real_time_refresh=True),
        MessageTextInput(name="server_url", display_name="HTTP Endpoint", placeholder="http://localhost:3001", info="HTTP endpoint for the MCP server", show=True, real_time_refresh=True),
        DictInput(name="headers", display_name="Headers", value={}, show=False, advanced=True),
        IntInput(name="timeout_seconds", display_name="Timeout (seconds)", value=30, advanced=True),
        DropdownInput(name="selected_tools", display_name="Selected Tools", options=["all"], value="all", show=False, real_time_refresh=True)
    ]

    outputs = [Output(display_name="Tools", name="tools", method="build_output")]

    async def update_tool_list(self):
        try:
            if self.connection_type == "http":
                self.tools = await self.client.connect_http(self.server_url, getattr(self, "headers", {}), getattr(self, "timeout_seconds", 30))
            elif self.connection_type == "sse":
                self.tools = await self.client.connect_sse(self.server_url, getattr(self, "headers", {}), getattr(self, "timeout_seconds", 30))
            self._tool_cache = {tool.name: tool for tool in self.tools if hasattr(tool, "name")}
            return self.tools
        except Exception as e:
            logger.error(f"Failed to update tools: {e}")
            self.tools = []
            self._tool_cache = {}
            return []

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        try:
            if field_name == "connection_type":
                # Show appropriate URL field based on connection type
                if field_value == "http":
                    build_config["server_url"]["display_name"] = "HTTP Endpoint"
                    build_config["server_url"]["placeholder"] = "http://localhost:3001"
                    build_config["server_url"]["info"] = "HTTP endpoint for the MCP server"
                elif field_value == "sse":
                    build_config["server_url"]["display_name"] = "SSE Server URL"
                    build_config["server_url"]["placeholder"] = "http://localhost:3001/sse"
                    build_config["server_url"]["info"] = "SSE URL for the MCP server"

                build_config["server_url"]["show"] = True
                build_config["selected_tools"]["show"] = False
                build_config["selected_tools"]["options"] = ["all"]
                build_config["selected_tools"]["value"] = "all"

            elif field_name == "server_url" and field_value and field_value.strip():
                # Basic URL validation
                if not (field_value.startswith('http://') or field_value.startswith('https://')):
                    build_config["selected_tools"]["options"] = ["all", "❌ Invalid URL"]
                    build_config["selected_tools"]["value"] = "❌ Invalid URL"
                    build_config["selected_tools"]["show"] = True
                    return build_config

                try:
                    tools = await self.update_tool_list()
                    tool_names = [t.name for t in tools if hasattr(t, "name")]

                    # Add "all" option plus individual tools
                    build_config["selected_tools"]["options"] = ["all"] + tool_names
                    build_config["selected_tools"]["show"] = len(tool_names) > 0
                    build_config["selected_tools"]["value"] = "all"

                except Exception as e:
                    logger.error(f"Failed to update tool list: {e}")
                    build_config["selected_tools"]["show"] = True
                    build_config["selected_tools"]["options"] = ["all", "❌ Connection Failed"]
                    build_config["selected_tools"]["value"] = "❌ Connection Failed"

        except Exception as e:
            logger.error(f"Error updating build config: {e}")
        return build_config

    async def build_output(self) -> list[Tool]:
        """Build tools with SSE-optimized connection"""

        async def _build_with_sse_optimization():
            try:
                selected_tools = getattr(self, 'selected_tools', 'all')
                server_url = getattr(self, 'server_url', '')
                connection_type = getattr(self, 'connection_type', 'http')

                logger.info(f"Building MCP tools from {server_url} via {connection_type}")
                logger.info(f"Selected tools: {selected_tools}")

                if selected_tools in ["❌ Connection Failed", "❌ Invalid URL"]:
                    raise ValueError("Connection failed - check server URL")

                if not server_url or not server_url.strip():
                    raise ValueError("No server URL provided")

                # Use cached tools if available, otherwise connect
                if not self.tools:
                    self.tools = await self.update_tool_list()

                if not self.tools:
                    raise ValueError("No tools returned from server")

                # Filter tools based on selection
                if selected_tools == "all" or not selected_tools:
                    filtered_tools = self.tools
                else:
                    # Handle single tool selection
                    filtered_tools = []
                    for tool in self.tools:
                        if hasattr(tool, 'name') and tool.name == selected_tools:
                            filtered_tools.append(tool)

                if not filtered_tools:
                    raise ValueError(f"No tools found for selection: {selected_tools}")

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
                            continue

                if not tool_list:
                    raise ValueError("No tools were successfully created")

                tool_names = [tool.name for tool in filtered_tools]
                logger.info(f"Successfully created {len(tool_list)} tools: {tool_names}")
                return tool_list

            except Exception as e:
                logger.error(f"SSE-optimized build failed: {e}")
                raise ValueError(f"Build failed: {str(e)}")

        # Shield the build process with generous timeout for SSE issues
        try:
            return await asyncio.wait_for(
                asyncio.shield(_build_with_sse_optimization()),
                timeout=90  # Allow time for SSE retries (3 attempts × 35s max + buffer)
            )
        except asyncio.TimeoutError:
            error_msg = "Build timed out after 90s - SSE connection issues persist"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except asyncio.CancelledError:
            error_msg = "Build cancelled by Langflow"
            logger.warning(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Build failed: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def cleanup(self):
        """Cleanup for Langflow"""
        try:
            await self.client.exit_stack.aclose()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")